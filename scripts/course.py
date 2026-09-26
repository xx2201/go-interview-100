"""课程目录、发布与校验。仅使用 Python 标准库。"""
from pathlib import Path
import argparse
import re
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
MODULES = ['语言设计', '类型与内存', '并发编程', '运行时与性能', '后端接口', '数据库', '缓存与消息', '微服务', 'Kratos 工程', '生产与系统设计']
ROWS = [line.split('\t') for line in (ROOT / 'docs/catalog.tsv').read_text(encoding='utf-8').splitlines()]
HEADINGS = ['## 简短回答', '## 详细解析', '## 常见误区 / 面试追问', '## 参考资料']

def path(row):
    return Path(row[1]) / f'{row[0]}-{row[4]}.md'

def run(args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=180)
    if result.returncode:
        raise RuntimeError(f'{args!r}\n{result.stdout}\n{result.stderr}')
    return result.stdout

def check_article(row, execute=False, race=False):
    p = ROOT / path(row)
    body = p.read_text(encoding='utf-8')
    assert body.startswith(f'# {row[0]} '), f'{p}: 题号不符'
    assert all(body.count(h) == 1 for h in HEADINGS), f'{p}: 四段式不完整'
    assert [body.index(h) for h in HEADINGS] == sorted(body.index(h) for h in HEADINGS), f'{p}: 段落顺序异常'
    assert row[3] in body.splitlines()[0], f'{p}: 标题与目录不一致'
    assert body.count('```') % 2 == 0, f'{p}: 代码围栏未闭合'
    assert len(re.findall(r'[\u4e00-\u9fff]', body)) >= 450, f'{p}: 内容不足'
    assert not re.search(r'\bTODO\b|\bTBD\b|待补充|待完善', body), f'{p}: 含占位内容'
    assert re.search(r'\]\(https://', body), f'{p}: 缺少资料链接'
    assert re.search(r'```mermaid\n.+?```', body, re.S), f'{p}: 缺少课程图解'
    blocks = re.findall(r'```go\n(.*?)```\s*```output\n(.*?)```', body, re.S)
    assert len(blocks) == len(re.findall(r'```go\n', body)), f'{p}: Go 示例缺少预期输出'
    if execute:
        work = ROOT / '.work'
        work.mkdir(exist_ok=True)
        for code, expected in blocks:
            with tempfile.TemporaryDirectory(dir=work) as temp:
                source = Path(temp) / 'main.go'
                source.write_text(code, encoding='utf-8')
                actual = run(['go', 'run', *(['-race'] if race else []), str(source)])
                assert actual.strip() == expected.strip(), f'{p}: 输出不符: {actual!r}'
    return len(blocks)

def readme():
    intro = '''# Go Backend Interview 100

从语言设计到生产系统：用 100 个问题建立 Go 后端知识体系。

本项目面向掌握基本语法、准备后端面试或希望补齐工程能力的开发者。每题先回答核心问题，再通过机制、具体场景、取舍、误区与追问形成完整解释。代码题附可执行示例和预期输出，系统设计题写清假设、失败路径和验证方法。

**100 / 100 题已完成深化，每题都有图解，并保留首次创作与深化两轮独立提交。** [可运行的 Kratos HTTP/gRPC 服务](examples/catalog/README.md)把协议、业务、仓储、中间件与生命周期串成完整示例。

课程包含可执行 Go 示例、Review 修复前后对照、带前提的容量与故障推演，以及综合追问评分。图解采用 GitHub 可直接显示的 Mermaid，便于跟随请求、状态和资源生命周期阅读。第二轮范围与进度见 [深化计划](docs/DEEPENING_PLAN.md)，与参考项目的具体对照见 [行文思路核查](docs/STYLE_REVIEW.md)。

## 知识地图

```mermaid
flowchart LR
    A[语言设计] --> B[类型与内存]
    B --> C[并发编程]
    C --> D[运行时与性能]
    D --> E[后端接口]
    E --> F[数据库]
    F --> G[缓存与消息]
    G --> H[微服务]
    H --> I[Kratos 工程]
    I --> J[生产与系统设计]
```

## 怎样使用

1. 先用一到两分钟口述答案，再阅读「简短回答」。
2. 跟着「详细解析」推演一次请求或一次故障，运行代码并核对输出。
3. 遮住答案回答追问，记录自己漏掉的边界，而不是背诵术语。
4. 用关联题补全依赖知识，用官方资料核对项目实际版本。

先读图中的对象与箭头，再回答「在哪一步失败会留下什么状态」。030 的竞态反例单独标注，098 的错误起点仅用于复现输入缺陷；不要把反例当成可复用的正确实现。

学习路线：入门按 001–030 → 041–052 → 081–085；后端工程按 041–080 → 091–095；性能专项按 017–018 → 025–040 → 060、070；Kratos 专项先读 005、009、026、050、071–079，再读 081–090。综合复习用 096–100。

## 版本与验证

示例基线为 Go 1.26，编写环境为 Go 1.26.5 / Windows amd64。语言保证、工具链实现和工程建议在正文中分别说明。标准库示例可将完整 Go 代码块保存为 main.go 后运行 `go run main.go`；依赖 Kratos 的示例需在本仓库根目录运行，以使用锁定的模块依赖。SQL、配置和架构步骤用于说明明确场景，不宣称已在真实集群中验证。

运行 `python scripts/course.py check --execute` 检查全部课程、站内链接并执行文章中的 Go 示例。完整验证记录见 [验收记录](docs/VALIDATION.md)。课程计划及逐题进度见 [PLAN.md](PLAN.md)。

## 100 题目录

'''
    for i, name in enumerate(MODULES):
        intro += f'### {i + 1:02d} · {name}\n\n| 题号 | 难度 | 问题 |\n| --- | --- | --- |\n'
        for row in ROWS[i * 10:(i + 1) * 10]:
            intro += f'| {row[0]} | {row[2]} | [{row[3]}]({path(row).as_posix()}) |\n'
        intro += '\n'
    intro += '''## 写作与来源

组织形式参考 [BigKunLun/Agent-Interview-100](https://github.com/BigKunLun/Agent-Interview-100)：问题驱动、主题分层、四段式文章、场景题和递进追问。本仓库的 Go 选题、解析与示例为独立编写，未复制参考仓库的正文或图片。

每篇参考资料优先采用语言规范、标准库文档和组件官方文档。不要把运行时实现细节当作语言承诺，也不要把单机示例当作生产系统的全部实现。勘误时请同时给出课程题号、实际版本和可复现证据。
'''
    (ROOT / 'README.md').write_text(intro, encoding='utf-8')

def progress():
    p = ROOT / 'PLAN.md'
    body = p.read_text(encoding='utf-8')
    pre = body.split('## 逐题进度')[0]
    entries = '\n'.join(f'- [{"x" if (ROOT / path(r)).exists() else " "}] {r[0]} {r[3]}' for r in ROWS)
    p.write_text(pre + '## 逐题进度\n\n' + entries + '\n', encoding='utf-8')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['init', 'check', 'publish', 'deepen'])
    parser.add_argument('ids', nargs='*')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--race', action='store_true', help='执行 Go 示例并启用 race detector')
    args = parser.parse_args()
    if args.action == 'init':
        readme()
        progress()
        return
    selected = [r for r in ROWS if not args.ids or r[0] in args.ids]
    assert len(selected) == (len(args.ids) if args.ids else 100), '题号无效或重复'
    examples = 0
    for row in selected:
        examples += check_article(row, args.execute or args.race, args.race)
        if args.action in ('publish', 'deepen'):
            if args.action == 'deepen':
                assert '```mermaid\n' in (ROOT / path(row)).read_text(encoding='utf-8'), f'{row[0]}: 深化课程缺少图解'
            # 每次只暂存当前课程；不把其他已写文件带入该课程提交。
            assert not run(['git', 'diff', '--cached', '--name-only']).strip(), '暂存区非空'
            run(['git', 'add', '--', path(row).as_posix()])
            staged = run(['git', 'diff', '--cached', '--name-only']).splitlines()
            assert staged == [path(row).as_posix()], f'提交范围异常: {staged}'
            prefix = 'course' if args.action == 'publish' else 'deepen'
            print(run(['git', 'commit', '-m', f'docs({prefix}-{row[0]}): {row[3]}']).splitlines()[0], flush=True)
    if not args.ids:
        assert [r[0] for r in ROWS] == [f'{i:03d}' for i in range(1, 101)], '目录题号不连续'
        assert len(list(ROOT.glob('[0-9][0-9]-*/*.md'))) == 100, '课程数不等于 100'
        for p in ROOT.rglob('*.md'):
            if '.work' in p.parts:
                continue
            # 代码围栏和行内代码不属于 Markdown 链接，避免把泛型签名识别为链接。
            prose = re.sub(r'```.*?```', '', p.read_text(encoding='utf-8'), flags=re.S)
            prose = re.sub(r'`[^`\n]*`', '', prose)
            for target in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)', prose):
                if '://' not in target and not target.startswith('#'):
                    assert (p.parent / target.split('#')[0]).exists(), f'{p}: 断链 {target}'
        commits = run(['git', 'log', '--format=%H%x09%s']).splitlines()
        for row in ROWS:
            for prefix in ('course', 'deepen'):
                matches = [line.split('\t')[0] for line in commits if f'docs({prefix}-{row[0]}):' in line]
                assert len(matches) == 1, f'{row[0]}: 应有且只有一个 {prefix} 课程提交'
                files = run(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', matches[0]]).splitlines()
                assert files == [path(row).as_posix()], f'{row[0]}: {prefix} 提交混入其他文件'
        print('通过：站内链接、100 篇图解与两轮各 100 个独立课程提交')
    print(f'通过：{len(selected)} 题，{examples} 个 Go 示例' + ('（已运行并比对输出）' if args.execute or args.race else '（仅结构检查）'))

if __name__ == '__main__':
    main()
