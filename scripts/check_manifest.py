"""Verify bundled public source files against recorded hashes."""
import hashlib
import json
from pathlib import Path
root = Path(__file__).resolve().parents[1] / 'data/raw'
manifest = json.loads((root/'manifest.json').read_text())
for name, expected in manifest['files_sha256'].items():
    actual = hashlib.sha256((root/name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f'Hash mismatch: {name}')
print('All three public source hashes match.')
