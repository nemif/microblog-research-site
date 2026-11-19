"""Reproducible CSV -> Markdown + SVG pipeline, with content-hash cache."""
import csv
import hashlib
import json
import os
import subprocess
import sys
import datetime
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data' / 'historical_measurements.csv'
TARGET = ROOT / 'docs' / 'results.md'
FIGURE = ROOT / 'docs' / 'assets' / 'lcp.svg'
CACHE = ROOT / '.cache' / 'generation.json'
BUILD_INFO = ROOT / 'docs' / 'build-info.md'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def revision():
    try:
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, stderr=subprocess.DEVNULL, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return 'git-репозиторий пока не создан'


def build_metadata():
    # Always regenerate publication metadata, including on a cache hit.
    # Scientific numeric outputs are kept separate from a volatile timestamp.
    commit = os.environ.get('GITHUB_SHA') or revision()
    date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    source_hash = sha256(SOURCE)
    lines = [
        '# Метаданные сборки', '',
        '| Поле | Значение |', '| --- | --- |',
        f'| Git-коммит | `{commit}` |',
        f'| Дата сборки (UTC) | {date} |',
        '| Версия датасета | `nir2-summary-v1` |',
        f'| SHA-256 CSV | `{source_hash}` |',
        '',
        '> Исторические данные: второй этап НИР. Дата публикации не является датой измерений.',
    ]
    BUILD_INFO.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('BUILD METADATA: обновлены SHA, время сборки и версия данных')


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    digest = hashlib.sha256((sha256(SOURCE) + sha256(Path(__file__)) + matplotlib.__version__).encode()).hexdigest()
    if CACHE.exists() and TARGET.exists() and FIGURE.exists() and json.loads(CACHE.read_text(encoding='utf8')).get('digest') == digest:
        print('CACHE HIT: данные не изменились; пересчёт и график пропущены')
        build_metadata()
        return
    with SOURCE.open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    required = {'version','description','score','lcp_s','fcp_s','tbt_ms','cls','si_s','origin'}
    if len(rows) != 3 or any(not required.issubset(row) for row in rows):
        raise ValueError('Ожидаются 3 записи с полными столбцами')
    versions = []
    lcp = []
    for row in rows:
        for key in ['score','lcp_s','fcp_s','tbt_ms','cls','si_s']:
            v = float(row[key])
            if not 0 <= v < 100000:
                raise ValueError(f'Некорректное значение {key} для {row["version"]}')
        versions.append(row['version'])
        lcp.append(float(row['lcp_s']))
    fig, ax = plt.subplots(figsize=(8,4.25))
    bars = ax.bar(versions, lcp, color=['#7c83a4','#6675c9','#4eafad'])
    for bar, v in zip(bars, lcp):
        ax.text(bar.get_x()+bar.get_width()/2, v+0.08, f'{v:.2f} c', ha='center', fontsize=10)
    ax.set_ylabel('LCP, секунды')
    ax.set_title('Исторические средние значения LCP по версиям MicroBlog')
    ax.set_ylim(0, max(lcp)*1.18)
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout()
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE, format='svg', bbox_inches='tight')
    plt.close(fig)
    values = ['version','score','lcp_s','fcp_s','tbt_ms','cls','si_s']
    labels = ['Версия','Score','LCP, c','FCP, c','TBT, мс','CLS','SI, c']
    lines=['# Результаты исследования','',
           '> Источник: сводные таблицы НИР, этап 2. Это архивные данные, а не новый эксперимент.','',
           '| ' + ' | '.join(labels) + ' |', '|' + '|'.join(['---']*len(labels)) + '|']
    for row in rows:
        lines.append('| ' + ' | '.join(row[k] for k in values) + ' |')
    lines += ['', '![Средние значения LCP](assets/lcp.svg)', '',
              '## Интерпретация', '',
              'По сводным измерениям v2 и v3 значительно быстрее базовой реализации по LCP. '
              'Однако несколько оптимизаций изменялись одновременно, поэтому причинный вклад отдельно WebP, '
              'lazy loading и AVIF этим сравнением не установлен.', '',
              '## Происхождение данных и воспроизводимость сборки', '',
              f'- SHA-256 исходного CSV: `{sha256(SOURCE)}`.',
              f'- Версия исходного кода (Git): `{revision()}`.',
              '- Сборка с одинаковым CSV и генератором должна создавать одинаковые числовые таблицы. '
              'Дата сборки намеренно не вшита в Markdown для детерминированности.', '',
              'Первичные измерения, условия теста и ограничения см. в отчёте НИР, этап 2.']
    TARGET.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps({'digest': digest, 'source_sha256':sha256(SOURCE)}, indent=2), encoding='utf8')
    print('CACHE MISS: CSV обработан, результаты и SVG обновлены')
    build_metadata()

if __name__ == '__main__':
    main()
