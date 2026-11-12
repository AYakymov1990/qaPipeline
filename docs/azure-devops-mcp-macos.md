# Azure DevOps MCP на macOS — встановлення

Claude Code на Mac отримує задачі з Azure DevOps (організація `abp`, проєкт `Avto.Pro`) через офіційний MCP-сервер Microsoft. Тільки читання: інструменти запису заборонені в `.claude/settings.json`. У пісочниці сервер не працює — це очікувано.

## 1. Node.js 20+

```bash
node -v
```

- `v20` або новіша — далі.
- Немає або старіша: `brew install node` (або `brew upgrade node`), потім знову `node -v`.

## 2. Оновити pipeline

```bash
cd ~/Desktop/ABP/avto/qaPipeline-repo
git status            # незакомічені файли — спершу закомітьте
git pull
```

## 3. Запустити Claude Code і дозволити сервер

```bash
claude
```

- На питання про MCP-сервери з `.mcp.json` — дозволити `azure-devops` (і `playwright`).
- Питання не було або колись відмовили: вийти (`/exit`), виконати `claude mcp reset-project-choices`, знову `claude`.

## 4. Перевірити підключення

У Claude Code: `/mcp` — у списку `azure-devops`. Перший запуск довший: `npx` завантажує пакет.

## 5. Увійти в Azure DevOps

У Claude Code:

```text
покажи назву і стан задачі 129318
```

Відкриється браузер — увійдіть акаунтом Microsoft, що має доступ до `dev.azure.com/abp`, поверніться в термінал. Має прийти назва і стан задачі.

## 6. Робота

- Нова задача: `/qa-pipeline <ID>` — сам забере задачу з Azure DevOps.
- Оновити задачу (нові коментарі, зміни опису): `/qa-ado-fetch <ID>`.

## Проблеми

| Симптом | Що робити |
| --- | --- |
| `npx: command not found` або помилка версії Node | Крок 1 |
| `azure-devops` немає в `/mcp` | `git pull` (крок 2), перезапуск `claude`; не допомогло — `claude mcp reset-project-choices` |
| Браузер не відкрився / вхід не проходить | Вхід через Azure CLI: `brew install azure-cli`, `az login`; у `.mcp.json` до аргументів `azure-devops` додати `"--authentication", "azcli"` |
| `401` / `403` / задачу не знайдено | Акаунт без доступу до організації `abp` або проєкту `Avto.Pro` — увійти іншим акаунтом |
| Агент намагається щось змінити в задачі | Заборонено налаштуваннями; перевірити `/permissions` — правила `deny` для `mcp__azure-devops__…` |
