"""用已固定版本的工具重新生成课程示例协议；不进行全局安装。"""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def run(args):
    return subprocess.run(args, cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()

for tool, expected in [('protoc', 'libprotoc 29.3'), ('protoc-gen-go', 'v1.36.2'),
                       ('protoc-gen-go-grpc', '1.5.1'), ('protoc-gen-go-http', 'v2.9.2')]:
    actual = run([tool, '--version'])
    if actual.split()[-1] != expected.split()[-1]:
        raise RuntimeError(f'{tool}: expected {expected}, got {actual}')

module = run(['go', 'list', '-m', '-f', '{{.Dir}}', 'github.com/go-kratos/kratos/v2'])
run(['protoc', '--proto_path=.', f'--proto_path={Path(module) / "third_party"}',
     '--go_out=paths=source_relative:.', '--go-grpc_out=paths=source_relative:.',
     '--go-http_out=paths=source_relative:.', 'examples/catalog/api/catalog.proto'])
run(['gofmt', '-w', 'examples/catalog/api'])
print('Generated catalog protocol with pinned tool versions.')
