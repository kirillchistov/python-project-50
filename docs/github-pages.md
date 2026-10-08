# Публикация кабинета на GitHub Pages

GitHub Pages отдаёт только статику, без FastAPI. Поэтому перед выкладкой кабинет собирается в каталог `site/`: HTML уроков, CSS/JS и клиентские трассеры алгоритмов. Локально по-прежнему можно запускать `make dsa-lab` с живым API.

## Что уже лежит в репозитории

- [`.github/workflows/github-pages.yml`](../.github/workflows/github-pages.yml) — сборка и деплой
- `python -m dsa_lab.export_static` — генерация `site/`
- `web/static/js/tracers.js` — те же площадки, но в браузере (на Pages нет `POST /api/trace`)

Каталог `site/` в git не коммитится: его собирает Actions.

## Разовая настройка на GitHub

Это нужно сделать один раз в интерфейсе репозитория. Коммит workflow можно сделать отдельно.

1. **Settings → Pages**
2. **Build and deployment → Source:** `GitHub Actions` (не «Deploy from a branch»)
3. Если появится environment `github-pages`, оставьте его. Для публичного репозитория дополнительных секретов не нужно.
4. Закоммитьте и запушьте workflow (ветка `main` или `master`) либо запустите **Actions → GitHub Pages → Run workflow**.
5. Дождитесь зелёного job `deploy`. Ссылка появится в **Settings → Pages** и в environment `github-pages`.

Ожидаемый адрес для этого репозитория:

`https://<username>.github.io/python-project-50/`

Пример: `https://kirillchistov.github.io/python-project-50/`

## Если страница пустая или «ломаются» стили

Частая причина — неверный префикс URL. Для project-сайта (`username.github.io/имя-репо/`) сборка сама подставляет `/имя-репо`.

Переопределить можно вручную: **Actions → GitHub Pages → Run workflow → base_path**.

| Случай | `base_path` |
|---|---|
| Репозиторий `python-project-50` | оставьте пустым (возьмётся `/python-project-50`) |
| Сайт пользователя `username.github.io` | `/` |
| Свой домен, сайт в корне | `/` |

После смены имени репозитория просто перезапустите workflow.

## Локальная проверка той же статики

```bash
make install
make dsa-pages
make dsa-pages-preview
```

Откройте [http://127.0.0.1:8080](http://127.0.0.1:8080). Для проверки префикса как на Pages:

```bash
DSA_BASE_PATH=/python-project-50 poetry run python -m dsa_lab.export_static --out site
```

Тогда превью через `http.server` из `site/` не подойдёт: браузер будет ходить в `/python-project-50/...`. Для такой проверки удобнее открыть уже задеплоенный Pages.

## Что не трогает Hexlet

Workflow `hexlet-check.yml` и `make check` не зависят от Pages. CLI `gendiff` по-прежнему проверяется отдельно.
