# Артефакти задач

Одна папка на задачу: `work/<ID>/`, де ID — номер задачі в Azure DevOps або коротка назва латиницею.

```
work/<ID>/
├── 00-input/
│   ├── requirement.md      опис задачі з Azure DevOps дослівно + посилання на Figma
│   ├── comments.md         коментарі задачі (автор, дата)
│   ├── grooming-YYYY-MM-DD.md  транскрипції грумінгів
│   ├── notes.md            контекст з особистих повідомлень
│   ├── code-changes.md     що реально змінено в коді (qa-code-changes)
│   ├── autotests-coverage.md  покриття регресу автотестами (qa-autotests-coverage)
│   └── test-data.md        стенд, акаунти (назви змінних з .env) і дані під задачу — вказує QA
├── 01-review.md            ревʼю вимог: дефекти RD, питання Q, промпти пошуку
├── 01-answers.md           відповіді на питання (заповнює QA)
├── 02-spec.md              тестова специфікація: REQ і критерії AC
├── 03-checklist.xlsx       чек-лист для людей
├── 03-checklist.md         чек-лист — джерело правди: CHK
├── 03-dev-checklist.md     чек-лист для розробника: DEV
├── 04-cases/
│   ├── _index.md           перелік кейсів
│   └── TC-001.md …         кейси для агента
├── 05-runs/
│   └── YYYY-MM-DD-HHMM/
│       ├── report.md       звіт прогону
│       └── TC-001/ …       скріншоти (не комітяться)
├── pipeline.md             маршрут, журнал, «де зупинились»
├── context-candidates.md   кандидати в контекст, які чекають відповіді QA
└── bugs/
    └── BUG-001.md …        баг-репорти
```

Шаблони кожного файлу — у `templates/` відповідного скіла в `.claude/skills/`.

Наскрізні ID: S (твердження) → RD / Q → REQ / AC → CHK → TC → BUG.
