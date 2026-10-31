"""Exercise installed core, GUI, SDK, and CLI together on a real local server."""
import argparse
import importlib
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
from threading import Thread
import time

import torch
import uvicorn

import p2i
from p2i_gui import create_app
from p2i_sdk import Client


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--installed-root', type=Path)
    args = parser.parse_args()
    if args.installed_root:
        for name in ('p2i', 'p2i_gui', 'p2i_sdk', 'p2i_cli'):
            location = Path(importlib.import_module(name).__file__).resolve()
            assert location.is_relative_to(args.installed_root.resolve()), (name, location)
    model = torch.nn.Sequential(torch.nn.Linear(4, 8), torch.nn.ReLU(), torch.nn.Linear(8, 2)).eval()
    inputs = (torch.randn(2, 4),)
    harness = p2i.Harness(model, example_inputs=inputs)
    with socket.socket() as sock, tempfile.TemporaryDirectory() as folder:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(create_app(harness), log_level='error'))
        thread = Thread(target=server.run, kwargs={'sockets': [sock]}, daemon=True)
        thread.start()
        try:
            for _ in range(100):
                if server.started:
                    break
                time.sleep(0.05)
            else:
                raise RuntimeError('Local API failed to start')
            client = Client(f'http://127.0.0.1:{port}', timeout=60)
            action = {'type': 'batch', 'expected_revision': 0, 'actions': [
                {'type': 'set_parameter', 'target': '0', 'parameter': 'out_features', 'value': 6},
                {'type': 'set_parameter', 'target': '2', 'parameter': 'in_features', 'value': 6},
            ]}
            assert client.command('apply', action)['result']['committed']
            assert client.command('retrace')['result']['success']
            checkpoint = client.save_checkpoint(Path(folder) / 'model.p2i', expected_revision=1)
            assert client.command('undo')['result']['success']
            assert client.open_checkpoint(checkpoint)['state']['summary']['revision'] == 1
            independent = p2i.load_model(checkpoint)
            assert independent[0].out_features == 6
            optimizer = torch.optim.SGD(independent.parameters(), lr=0.1)
            optimizer.zero_grad()
            independent(*inputs).square().mean().backward()
            optimizer.step()
            result = subprocess.run([sys.executable, '-m', 'p2i_cli', 'open', str(checkpoint), '--no-serve'],
                                    text=True, capture_output=True, timeout=90)
            assert result.returncode == 0, result.stdout + result.stderr
        finally:
            server.should_exit = True
            thread.join(timeout=10)
    print('PASS installed core + GUI + SDK + CLI: edit, retrace, download, undo, restore, train, reopen')


if __name__ == '__main__':
    main()
