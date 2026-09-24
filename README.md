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
