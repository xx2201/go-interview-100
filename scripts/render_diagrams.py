"""把指定课程的全部 Mermaid 实际渲染到 .work，验证语法并供目视检查。"""
from pathlib import Path
import argparse
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('ids', nargs='*', help='三位题号；省略时检查全部课程')
parser.add_argument('--cli', type=Path, default=ROOT / '.work/diagram-tools/node_modules/@mermaid-js/mermaid-cli/src/cli.js')
args = parser.parse_args()
rows = [line.split('\t') for line in (ROOT / 'docs/catalog.tsv').read_text(encoding='utf-8').splitlines()]
selected = [r for r in rows if not args.ids or r[0] in args.ids]
assert len(selected) == (len(args.ids) if args.ids else 100), 'Invalid or duplicate course IDs'
if not args.cli.is_file():
    raise SystemExit('Install locally: npm install --prefix .work/diagram-tools --save-exact @mermaid-js/mermaid-cli@11.12.0')
parts = []
count = 0
for row in selected:
    source = ROOT / row[1] / f'{row[0]}-{row[4]}.md'
    diagrams = re.findall(r'```mermaid\n(.*?)```', source.read_text(encoding='utf-8'), re.S)
    assert diagrams, f'{source}: missing diagram'
    for i, diagram in enumerate(diagrams, 1):
        count += 1
        parts.append(f'## {row[0]} / {i}\n\n```mermaid\n{diagram}```\n')
target = ROOT / '.work/diagrams' / ('all' if not args.ids else '-'.join(args.ids))
target.mkdir(parents=True, exist_ok=True)
input_file = target / 'source.md'
input_file.write_text('\n'.join(parts), encoding='utf-8')
subprocess.run(['node', str(args.cli.resolve()), '-i', str(input_file), '-o', str(target / 'rendered.md'), '-e', 'png', '-b', 'white'], cwd=ROOT, check=True)
print(f'Rendered {count} diagrams from {len(selected)} courses: {target}')
