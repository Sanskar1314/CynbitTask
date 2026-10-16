"""Check local document links and PDF heading coverage; visual QA remains separate."""
from pathlib import Path
import json
import re
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]

def canon(value):
    return re.sub(r'[^a-z0-9]', '', value.lower())

if __name__ == '__main__':
    failures = []
    for path in [ROOT/'README.md', *list((ROOT/'docs').glob('*.md')), *list((ROOT/'reports').glob('*.md'))]:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if target.startswith(('http:', 'https:', '#')):
                continue
            if not (path.parent/target.split('#')[0]).exists():
                failures.append(f'Broken link in {path.name}: {target}')
    results = {}
    for name in ['AI_Opportunity_Report','Technical_Approach_Report','Complete_Project_Explanation']:
        source = ROOT/'reports'/f'{name}.md'
        pdf = PdfReader(source.with_suffix('.pdf'))
        text = '\n'.join(p.extract_text() or '' for p in pdf.pages)
        headings = re.findall(r'^#+ (.+)$', source.read_text(), re.M)
        missing = [h for h in headings if canon(h) not in canon(text)]
        failures.extend(f'Missing PDF heading: {name}: {h}' for h in missing)
        results[name] = {'pages':len(pdf.pages),'headings_checked':len(headings),
                         'missing_headings':missing,'extracted_characters':len(text),
                         'blank_pages':[i+1 for i,p in enumerate(pdf.pages) if not (p.extract_text() or '').strip()]}
    result = {'pdf_checks':results,'broken_links_or_missing_headings':failures}
    (ROOT/'evaluation/deliverable_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if failures:raise SystemExit(1)
