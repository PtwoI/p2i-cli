# p2i-cli

Command-line interface for P2I. Installs the `p2i` terminal command without
duplicating the analyzer or web server.

For local development, install `p2i-core`, then `p2i-gui`, then this package
with `python -m pip install -e .`. From an installed distribution:

```bash
p2i --help
p2i demo mlp --no-serve --save mlp.json
p2i demo cnn --no-serve --save cnn.json
p2i demo transformer --edit
p2i serve mlp.json
p2i harness inspect architecture.json
p2i skills list
```

The existing JSON actions and command names are preserved. Model analysis,
actions and skills come from `p2i-core`; serving comes from `p2i-gui`.

## Model checkpoints

```bash
python -m p2i_cli demo transformer --no-serve --checkpoint original.p2i
python -m p2i_cli checkpoint inspect original.p2i
python -m p2i_cli checkpoint apply original.p2i action.json --output edited.p2i
python -m p2i_cli checkpoint validate edited.p2i --backward
python -m p2i_cli open edited.p2i
```

Unlike architecture JSON, a checkpoint carries weights and examples across
processes. `open --no-serve --save-ir observed.json` refreshes runtime evidence
without starting a server. Validation and failed edits return nonzero exit
codes. Standard registered modules and bundled demos reopen independently;
custom Python forwards must be restored through `p2i.Harness.load` with a
matching `model=` template or a reconstruction adapter.

Run `python -m pytest -q`. The tests exercise save/edit/validate/open across
fresh subprocesses for MLP, CNN, and Transformer models.
