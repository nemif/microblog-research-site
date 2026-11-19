"""Run one cache miss and one cache hit and record accurate wall clock times."""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache' / 'generation.json'
CACHE.unlink(missing_ok=True)
records = []
for kind in ['MISS', 'HIT']:
    started = time.perf_counter()
    completed = subprocess.run([sys.executable, 'scripts/generate_results.py'], cwd=ROOT, capture_output=True, text=True)
    elapsed = time.perf_counter() - started
    print(f'{kind}: {elapsed:.3f} seconds, exit={completed.returncode}')
    print(completed.stdout)
    if completed.returncode:
        print(completed.stderr, file=sys.stderr)
        raise SystemExit(completed.returncode)
    if f'CACHE {kind}:' not in completed.stdout:
        raise RuntimeError('Cache state mismatch; see output above')
    records.append({'cache': kind, 'seconds': round(elapsed, 3)})
output = ROOT / 'cache_benchmark.json'
output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Measurement file:', output)
