#!/usr/bin/env python3
"""Check required meeting deliverables and candidate order."""
import json, re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
report=json.loads((root/'output/qa/validation.json').read_text())
assert report['2026-12-02-Paper-Review']['pages']==6
assert report['2026-12-02-Research-Discussion']['pages']==10
text='\n'.join(report['2026-12-02-Research-Discussion']['page_text'])
assert [text.index(f'Topic {x}:') for x in 'ABC']==sorted(text.index(f'Topic {x}:') for x in 'ABC')
for f in ['2026-12-02-Paper-Review-Evidence.md','2026-12-02-Research-Discussion-Evidence.md','2026-12-02-Research-Discussion-SPEC.md','README.md']:
 assert (root/f).is_file(),f
print('PASS: expected page counts, A → B → C order, and required docs.')
