# Sample Apps

Small runnable Python applications built on top of the Open Data Products SDK.
They are examples for local testing and experimentation, not package entry
points.

## ODP Document Inspector CLI

Inspect any ODPS, ODPC, ODPG, or ODPV YAML/JSON document:

```bash
python3 apps/document_inspector/cli.py examples/demo_product.yaml
python3 apps/document_inspector/cli.py examples/demo_product.yaml --json
```

The app reports detected spec and kind, validation status, a compact
explanation, discovered references, and bundled SDK resources.
