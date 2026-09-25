"""检查课程 HTTPS 参考链接可达性；网络失败不等同于资料失效。"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]
links = {}
for file in ROOT.glob('[0-9][0-9]-*/*.md'):
    for url in re.findall(r'\]\((https://[^)]+)\)', file.read_text(encoding='utf-8')):
        links.setdefault(url.split('#')[0], []).append(file.relative_to(ROOT).as_posix())

def check(url):
    try:
        req = Request(url, headers={'User-Agent': 'GoInterview100-LinkCheck/1.0'})
        with urlopen(req, timeout=15) as response:
            return {'url': url, 'status': response.status, 'final_url': response.url, 'files': links[url]}
    except HTTPError as err:
        return {'url': url, 'status': err.code, 'error': str(err), 'files': links[url]}
    except Exception as err:
        return {'url': url, 'status': None, 'error': str(err), 'files': links[url]}

with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(check, sorted(links)))
target = ROOT / '.work' / 'references.json'
target.parent.mkdir(exist_ok=True)
target.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
failed = [r for r in results if r['status'] != 200]
print(f'参考链接：{len(results)}，HTTP 200：{len(results) - len(failed)}，需复核：{len(failed)}')
for result in failed:
    print(result['status'], result['url'], result.get('error', ''))
