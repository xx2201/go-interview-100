"""单独执行标记为 go-bad-race 的教学反例，确认竞态确实被检测到。"""
from pathlib import Path
import argparse
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('ids', nargs='*')
args = parser.parse_args()
rows = [line.split('\t') for line in (ROOT / 'docs/catalog.tsv').read_text(encoding='utf-8').splitlines()]
selected = [r for r in rows if not args.ids or r[0] in args.ids]
assert len(selected) == (len(args.ids) if args.ids else 100), 'Invalid or duplicate course IDs'
target = ROOT / '.work/bad-examples'
target.mkdir(parents=True, exist_ok=True)
count = 0
for row in selected:
    body = (ROOT / row[1] / f'{row[0]}-{row[4]}.md').read_text(encoding='utf-8')
    for i, code in enumerate(re.findall(r'```go-bad-race\n(.*?)```', body, re.S), 1):
        source = target / f'{row[0]}-{i}.go'
        source.write_text(code, encoding='utf-8')
        result = subprocess.run(['go', 'run', '-race', str(source)], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=120)
        output = result.stdout + result.stderr
        source.with_suffix('.log').write_text(output, encoding='utf-8')
        assert result.returncode != 0 and 'WARNING: DATA RACE' in output, f'{source}: expected race diagnostic missing; see log'
        count += 1
        print(f'{row[0]} / {i}: race detected as expected')
assert count, 'No explicitly marked race counterexamples found'
print(f'Validated {count} race counterexamples; logs: {target}')
