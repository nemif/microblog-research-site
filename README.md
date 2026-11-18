# ЛР1. Научный сайт на MkDocs

Готовая заготовка ЛР1: MkDocs + Material, Python CSV → Markdown + SVG с кэшем и GitHub Actions. Архивные измерения взяты из второго отчёта НИР; новых экспериментов этот проект не заявляет.

## Быстрый запуск на Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/generate_results.py
mkdocs build --strict
mkdocs serve
```

Откройте `http://127.0.0.1:8000/`. В PowerShell, если активация заблокирована политикой, используйте `.\.venv\Scripts\python.exe` и `.\.venv\Scripts\mkdocs.exe` без активации.

## GitHub Pages

1. Создайте **публичный** репозиторий `microblog-research-site`.
2. В `mkdocs.yml` укажите `site_url: https://ВАШ_ЛОГИН.github.io/microblog-research-site/` (замените логин).
3. Запушьте содержимое папки как корень репозитория:

```bash
git init
git add .
git commit -m "Initial research site"
git branch -M main
git remote add origin https://github.com/ВАШ_ЛОГИН/microblog-research-site.git
git push -u origin main
```

4. В **Settings → Pages → Build and deployment → Source** выберите **GitHub Actions**.
5. Откройте вкладку **Actions**, проверьте `Research site CI/CD`. После успеха сайт будет доступен по адресу из шага 2.
6. Для демонстрации P3 обновите CSV в отдельной ветке, сравните `CACHE MISS`/`CACHE HIT`, проведите pull request и merge.

## Helios (дополнительная доставка)

`.github/workflows/helios.yml` запускается вручную и требует Secrets: `HELIOS_HOST`, `HELIOS_USER`, `HELIOS_PATH`, `HELIOS_SSH_KEY`, `HELIOS_KNOWN_HOSTS`, `HELIOS_URL`. Нужны SSH-доступ из runner GitHub, разрешения на целевую папку и корректный публичный URL. `HELIOS_KNOWN_HOSTS` берётся из доверенного канала; не отключайте проверку ключа. Поскольку у обеих площадок могут быть разные URL и базовые пути, используется `use_directory_urls: false` и только относительные ссылки внутри сайта; отдельно проверьте все пути в подкаталоге.

## Что ещё обязательно для зачёта

- Реально опубликовать GitHub Pages и Helios/аналог, показать ссылки.
- Приложить успешный и намеренно проваленный запуск CI, три реальные ошибки с гипотезами и исправлениями.
- Измерить время и вес артефактов, проверить сайт без внешних CDN.
- Заполнить `REPORT_TEMPLATE.md` доказательствами, а не вымышленными скриншотами.

## Структура

- `data/` — опубликованные сводные измерения НИР;
- `scripts/` — генератор научных артефактов;
- `docs/` — Markdown-страницы и SVG;
- `.github/workflows/pages.yml` — обязательный GitHub CI/CD;
- `.github/workflows/helios.yml` — дополнительная выкладка по SSH;
- `REPORT_TEMPLATE.md` — черновик отчёта со списком требуемых доказательств.
