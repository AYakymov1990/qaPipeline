# Пісочниця для аналізу коду AvtoPro (macOS, Apple Silicon)

Claude Code працює в ізольованій пісочниці Docker Sandboxes (`sbx`): бачить тільки підключені папки, інтернет закритий, крім серверів Anthropic. Папка `qaPipeline-repo` підключена із записом (сюди пишуться артефакти), код AvtoPro і документація CodeWiki — **тільки для читання**.

Отримання задачі з Azure DevOps (`qa-ado-fetch`, MCP `azure-devops`) і прогін агентом у браузері (Playwright MCP) робляться **поза пісочницею** — у Claude Code на Mac: там працює IP з доступом до стендів і видно браузер. Обидві сесії пишуть в одну папку `qaPipeline-repo`.

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
├── AvtoPro/            git-репозиторій проєкту: гілка розробника (тільки читання в пісочниці)
├── AvtoProAutomation/  проєкт автотестів (тільки читання)
├── CodeWiki/           та сама репа, гілка docs/wiki-kb-pilot
│   └── CodeWiki/       сама вікі: kb/, tools/, README.md, AUTOUPDATE.md (підключається тільки вона)
└── qaPipeline-repo/    цей репозиторій
```

### CodeWiki — окрема робоча копія гілки документації (один раз)

Перевірте, чи вона вже є:

```bash
git -C ~/Desktop/ABP/avto/CodeWiki branch --show-current     # має бути docs/wiki-kb-pilot
```

Якщо папки немає — створіть її як `worktree` (окрема папка зі своєю гілкою, спільне сховище git):

```bash
cd ~/Desktop/ABP/avto/AvtoPro
git fetch
git worktree add ../CodeWiki docs/wiki-kb-pilot
```

- Переключення гілок і мерж master в `AvtoPro` папку `CodeWiki` не зачіпають, і навпаки.
- В `AvtoPro` не можна зробити `checkout docs/wiki-kb-pilot`, поки вона відкрита в `CodeWiki` — це й не потрібно.
- Оновити документацію: `git -C ~/Desktop/ABP/avto/CodeWiki pull`.
- Прибрати папку: `git -C ~/Desktop/ABP/avto/AvtoPro worktree remove ../CodeWiki`.

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
sbx run --name avtopro-qa claude \
  /Users/oleksandrpc/Desktop/ABP/avto/qaPipeline-repo \
  /Users/oleksandrpc/Desktop/ABP/avto/AvtoPro:ro \
  /Users/oleksandrpc/Desktop/ABP/avto/CodeWiki/CodeWiki:ro \
  /Users/oleksandrpc/Desktop/ABP/avto/AvtoProAutomation:ro
```

Підключається тільки вкладена папка з вікі: у корені робочої копії гілки документації є ще й код, який не стосується задачі.

Пісочниця вже створена з двома папками — щоб додати CodeWiki, спершу `sbx rm avtopro-qa` (файли не зачіпає), потім команда вище.

Усередині Claude Code: `/login`, потім `/status` — має бути підписка, а не «API Usage Billing». Питання про MCP-сервер `playwright` — можна відмовитись: браузер у пісочниці не потрібен.

Перевірка: `pwd` — папка `qaPipeline-repo`; спроба створити файл у `../AvtoPro` — помилка (тільки читання); `git -C ../AvtoPro --no-optional-locks diff --stat master...HEAD` — список змін розробника; `ls /Users/oleksandrpc/Desktop/ABP/avto/CodeWiki/CodeWiki/kb` — індекс документації.

## Щодня

```bash
git -C ~/Desktop/ABP/avto/CodeWiki pull          # свіжа документація
git -C ~/Desktop/ABP/avto/AvtoProAutomation pull # свіжі автотести
cd ~/Desktop/ABP/avto/qaPipeline-repo && sbx run avtopro-qa
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
