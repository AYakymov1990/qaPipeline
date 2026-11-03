# QA pipeline (AvtoPro)

Набір скілів Claude Code для QA: від ревʼю вимог до баг-репортів. Кожен етап читає спільний контекст проєкту (`qa-context/`) і пише артефакти в `work/<ID задачі>/`, повʼязані наскрізними ID: **REQ → CHK → TC → BUG**.

## Етапи

| Етап | Скіл | Що робить | Артефакт | Статус |
| --- | --- | --- | --- | --- |
| 0 | `prompts/build-context.md` | Збирає базовий контекст проєкту з документації | `qa-context/*` | готово |
| — | `qa-pipeline` | Визначає маршрут задачі (S / M / L) і наступний крок | `pipeline.md` | готово |
| 1 | `qa-req-review` | Ревʼю вимог: дефекти, питання, промпти для пошуку відповідей у документації | `01-review.md`, `01-answers.md` | готово |
| 2 | `qa-spec` | Тестова специфікація з REQ-ID і критеріями Given/When/Then | `02-spec.md` | готово |
| 3 | `qa-checklist` | Чек-лист від специфікації, ревʼю або задачі; правила якості й тест-дизайну | `03-checklist.md` → `03-checklist.xlsx` | готово |
| 3b | `qa-dev-checklist` | Чек-лист самоперевірки для розробника перед переведенням задачі в тест | `03-dev-checklist.md` | готово |
| 4a | `qa-agent-cases` | Кейси для агента з рядків «агент» чек-листа | `04-cases/TC-*.md` | готово |
| 4b | `qa-agent-run` | Прогін через Playwright MCP на тестовому стенді; тільки явний запуск `/qa-agent-run <ID>` | `05-runs/<дата>/` | готово |
| 5 | `qa-bug-report` | Баг-репорт: передумови, кроки, фактичний і очікуваний результат — для ручного перенесення в Azure DevOps | `bugs/BUG-*.md` | готово |

## Як почати

1. Встановіть [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) і відкрийте цю папку: `claude`.
2. Скопіюйте `.env.example` у `.env` і заповніть (файл не комітиться).
3. Покладіть документацію в `docs/technical/` і `docs/business/` (або додайте посилання в `qa-context/sources.md`).
4. Етап 0: базовий контекст уже зібрано. Дозаповніть прогалини промптом `prompts/fill-context-gaps.md` (Claude Code з доступом до CodeWiki: `claude --add-dir <шлях до CodeWiki>`) → перегляньте `git diff qa-context/` → закомітьте. `prompts/build-context.md` — для збору з нуля (новий проєкт).
5. Нова задача: `/qa-pipeline` + ID задачі — скіл визначить маршрут:
   - **S** (текст, верстка, одне поле) — одразу `/qa-checklist`;
   - **M** (кілька сценаріїв, ролей, площадок) — `/qa-req-review` → `/qa-checklist` → `/qa-dev-checklist`;
   - **L** (гроші, статуси, інтеграції, нова функціональність) — `/qa-req-review` → `/qa-spec` → `/qa-checklist` → `/qa-dev-checklist`.
6. Для xlsx потрібен Python 3 з `openpyxl`:
   ```bash
   python3 -m pip install --user openpyxl
   # якщо помилка externally-managed-environment (Python з Homebrew):
   python3 -m venv .venv && source .venv/bin/activate && pip install openpyxl
   ```
   З `.venv` — активуйте його (`source .venv/bin/activate`) перед запуском `claude`.

Playwright MCP підключається автоматично з `.mcp.json` (потрібен Node.js 18+).

## Структура

```
.claude/skills/        скіли pipeline
qa-context/            базовий контекст проєкту (читає кожен скіл)
prompts/               промпти, що запускаються вручну
docs/                  документація проєкту (технічна і бізнесова)
work/<ID>/             артефакти по задачі: 00-input/, 01-review.md, 01-answers.md, 02-spec.md …
examples/              еталонні результати етапів
```

## Правила

- Секрети тільки в `.env`. У скілах і контексті — лише назви змінних.
- Агент не працює з продом і не проводить реальні платежі.
- Між етапами — апрув QA. Баги в Azure DevOps заводить QA вручну.
