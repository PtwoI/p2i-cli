"""Checkpoint commands share the same model round trip as Python and the UI."""
import json
from pathlib import Path

import p2i


def add_commands(sub):
    root = sub.add_parser('checkpoint', help='Inspect, validate or edit a model checkpoint')
    commands = root.add_subparsers(dest='checkpoint_command', required=True)
    for name in ('inspect', 'validate', 'apply'):
        parser = commands.add_parser(name)
        parser.add_argument('file')
        if name == 'validate':
            parser.add_argument('--backward', action='store_true')
        if name == 'apply':
            parser.add_argument('action', help='Structured action JSON file')
            parser.add_argument('--output', required=True)


def run(args):
    try:
        harness = p2i.Harness.load(args.file)
        if args.checkpoint_command == 'inspect':
            result = {'summary': harness.observe(), 'architecture': harness.observe(level='architecture')}
            success = True
        elif args.checkpoint_command == 'validate':
            report = harness.validate(backward=args.backward)
            result = report.model_dump(mode='json')
            result['valid'] = report.valid
            success = report.valid
        else:
            action = json.loads(Path(args.action).read_text())
            result_object = harness.apply(action)
            result = result_object.model_dump(mode='json')
            success = result_object.success
            if success:
                harness.save(args.output)
        print(json.dumps(result, sort_keys=True))
        return 0 if success else 1
    except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
        print(json.dumps({'success': False, 'errors': [str(exc)]}))
        return 1
