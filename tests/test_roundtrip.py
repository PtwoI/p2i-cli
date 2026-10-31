import json
import subprocess
import sys

import pytest
import torch
import p2i


def cli(*arguments):
    return subprocess.run([sys.executable, '-m', 'p2i_cli', *map(str, arguments)],
                          text=True, capture_output=True, timeout=90)


@pytest.mark.parametrize('name', ['mlp', 'cnn', 'transformer', 'rnn', 'lstm', 'gru'])
def test_demo_checkpoint_edit_open_and_train(name, tmp_path):
    checkpoint = tmp_path / 'original.p2i'
    result = cli('demo', name, '--no-serve', '--checkpoint', checkpoint)
    assert result.returncode == 0, result.stderr
    target = {'mlp': 'layers.0', 'cnn': 'features.0', 'transformer': 'head', 'rnn': 'head', 'lstm': 'head', 'gru': 'head'}[name]
    action = tmp_path / 'action.json'
    action.write_text(json.dumps({'type': 'set_parameter', 'target': target,
                                  'parameter': 'bias', 'value': False}))
    edited = tmp_path / 'edited.p2i'
    result = cli('checkpoint', 'apply', checkpoint, action, '--output', edited)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)['committed']
    result = cli('checkpoint', 'validate', edited, '--backward')
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)['backward_valid']
    observation = tmp_path / 'observed.json'
    result = cli('open', edited, '--no-serve', '--save-ir', observation)
    assert result.returncode == 0, result.stdout + result.stderr
    assert p2i.load(observation).modules
    model = p2i.load_model(edited)
    assert model.get_submodule(target).bias is None


def test_errors_have_nonzero_exit_and_do_not_create_output(tmp_path):
    result = cli('open', tmp_path / 'missing.p2i', '--no-serve')
    assert result.returncode == 2 and 'p2i:' in result.stderr
    checkpoint = tmp_path / 'model.p2i'
    p2i.Harness(torch.nn.Linear(4, 2), example_inputs=(torch.ones(1, 4),)).save(checkpoint)
    action = tmp_path / 'bad.json'
    action.write_text(json.dumps({'type': 'set_parameter', 'target': 'a0',
                                  'parameter': 'in_features', 'value': 5}))
    output = tmp_path / 'rejected.p2i'
    result = cli('checkpoint', 'apply', checkpoint, action, '--output', output)
    assert result.returncode == 1
    assert not output.exists()
