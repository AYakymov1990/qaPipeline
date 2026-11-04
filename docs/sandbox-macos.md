# Пісочниця для аналізу коду AvtoPro (macOS, Apple Silicon)

Claude Code працює в ізольованій пісочниці Docker Sandboxes (`sbx`): бачить тільки підключені папки, інтернет закритий, крім серверів Anthropic. Папка `qaPipeline-repo` підключена із записом (сюди пишуться артефакти), код AvtoPro — **тільки для читання**.

Прогін агентом у браузері (Playwright MCP) робиться **поза пісочницею** — у Claude Code на Mac: там працює IP з доступом до стендів і видно браузер. Обидві сесії пишуть в одну папку `qaPipeline-repo`.

## Встановлення (один раз)

1. macOS 14 (Sonoma) або новіша, Apple Silicon: `sw_vers -productVersion`.
2. Homebrew — з [brew.sh](https://brew.sh), якщо ще немає.
3. Встановити і перевірити:
   ```bash
   brew trust docker/tap
   brew install docker/tap/sbx
   sbx version
   ```
4. Увійти в Docker: `sbx login`.
5. Мережева політика — все заборонено, крім Anthropic:
   ```bash
   sbx policy init deny-all
   sbx policy allow network "api.anthropic.com,claude.ai,platform.claude.com"
   sbx policy ls
   ```

## Структура папок

```
avto/
├── AvtoPro/            git-репозиторій проєкту (тільки читання в пісочниці)
└── qaPipeline-repo/    цей репозиторій
```

## Перед кожною задачею — гілка розробника

```bash
cd avto/AvtoPro
git checkout master && git pull
git checkout <гілка розробника> && git pull
git merge master --no-edit      # лише якщо потрібна свіжа збірка; для аналізу не обовʼязково
```

- Мерж локальний — не пушити в гілку розробника без домовленості.
- Конфлікти при мержі — `git merge --abort`, вирішує розробник.

## Перший запуск

```bash
cd avto/qaPipeline-repo
sbx run --name avtopro-qa claude . ../AvtoPro:ro
```

Усередині Claude Code: `/login`, потім `/status` — має бути підписка, а не «API Usage Billing». Питання про MCP-сервер `playwright` — можна відмовитись: браузер у пісочниці не потрібен.

Перевірка: `pwd` — папка `qaPipeline-repo`; спроба створити файл у `../AvtoPro` — помилка (тільки читання); `git -C ../AvtoPro --no-optional-locks diff --stat master...HEAD` — список змін розробника.

## Щодня

```bash
cd avto/qaPipeline-repo && sbx run avtopro-qa
```

Далі в Claude Code: `/qa-code-changes <ID>` або `/qa-pipeline <ID>`.

| Задача | Команда |
| --- | --- |
| Список пісочниць | `sbx ls` |
| Зупинити | `sbx stop avtopro-qa` |
| Видалити (файли не зачіпає) | `sbx rm avtopro-qa` |
| Продовжити розмову | `/resume` у Claude Code |

Папки пісочниця запамʼятовує при створенні. Перемістили `AvtoPro` чи `qaPipeline-repo` — `sbx rm avtopro-qa` і перший запуск заново.

## Проблеми

| Симптом | Що робити |
| --- | --- |
| `global network policy has not been initialized` | `sbx policy init deny-all`, потім `sbx policy allow network …` |
| `not a git repository` у AvtoPro | git-репозиторій в іншій папці (`find . -maxdepth 3 -name .git`) або склонуйте з Azure DevOps |
| `dubious ownership` усередині пісочниці | `git config --global --add safe.directory <шлях до AvtoPro>` |
| vim відкрився при `git merge` | `:wq` і Enter; наступного разу — `git merge master --no-edit` |
