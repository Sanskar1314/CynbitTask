"""Fetch only the named public UCI files; never extract arbitrary archive paths."""
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://archive.ics.uci.edu/static/public/331/sentiment+labelled+sentences.zip'
FILES = ['amazon_cells_labelled.txt', 'imdb_labelled.txt', 'yelp_labelled.txt']

if __name__ == '__main__':
    with urllib.request.urlopen(URL, timeout=60) as response:
        raw = response.read(2_000_000)
    archive = zipfile.ZipFile(io.BytesIO(raw))
    target = ROOT / 'data/raw'
    target.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name in FILES:
        matches = [p for p in archive.namelist() if p.endswith('/' + name)]
        if len(matches) != 1:
            raise ValueError(f'Unexpected archive layout for {name}')
        content = archive.read(matches[0])
        (target / name).write_bytes(content)
        hashes[name] = hashlib.sha256(content).hexdigest()
    (target / 'manifest.json').write_text(json.dumps({
        'url': URL, 'access_date': '2026-10-16',
        'archive_sha256': hashlib.sha256(raw).hexdigest(), 'files_sha256': hashes,
        'license': 'CC BY 4.0', 'creator': 'Dimitrios Kotzias (2015)',
        'doi': 'https://doi.org/10.24432/C57604'
    }, indent=2) + '\n')
    print(hashes)
