#!/usr/bin/env python3
"""Метрики QA pipeline з журналів Claude Code: час, токени, вартість, покриття.

Режими:
  mark   — позначка початку/кінця кейсу в прогоні:
           metrics.py mark --run work/<ID>/05-runs/<дата> --tc TC-001 --event start|end [--note "..."]
  run    — метрики прогону за позначками (marks.jsonl) → <run>/metrics.md
           metrics.py run --run work/<ID>/05-runs/<дата> --task <ID>
  task   — ретроспектива всієї задачі за журналами (етапи за скілами) → work/<ID>/metrics.md
           metrics.py task --task <ID>

Журнали: ~/.claude/projects/*/<session>.jsonl і <session>/subagents/*.jsonl.
Вартість — еквівалент за цінами Claude API (таблиця PRICES); частка підписки —
вартість періоду / вартість усіх сесій Claude Code на цьому компʼютері за 30 днів × ціна підписки.
Паролі й вміст повідомлень у звіт не потрапляють — лише числа й назви інструментів.
"""
import argparse, glob, json, os, re, sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

# $ за 1 млн токенів: input, output, cache read; запис у кеш = 1.25× (5 хв) / 2× (1 год) від input.
# Джерело: скіл claude-api (cached 2026-10-06). Оновлюйте при зміні цін.
PRICES = {
    'claude-opus-5-5': (4.00, 20.00, 0.20),
    'claude-opus-5': (5.00, 25.00, 0.50),
    'claude-fable-5-1': (10.00, 50.00, 0.25),
    'claude-sonnet-5-5': (2.00, 10.00, 0.20),
    'claude-sonnet-5': (2.00, 10.00, 0.20),
    'claude-haiku-5-5': (0.10, 0.50, 0.01),
    'claude-haiku-4-5': (1.00, 5.00, 0.10),
}
WEB_SEARCH_USD = 0.01  # $10 за 1000 запитів
SUBSCRIPTION_USD = float(os.environ.get('QA_SUBSCRIPTION_USD', '120'))
PROJECTS = os.path.expanduser('~/.claude/projects')
WAIT_CAP = timedelta(hours=2)  # довші паузи (ніч, перерва) не рахуються як очікування QA


def ts(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00')) if s else None


def price(model):
    for k, v in PRICES.items():
        if model and model.startswith(k):
            return v
    return PRICES['claude-opus-5-5']


def cost(u, model):
    pin, pout, pread = price(model)
    c5 = u.get('cw5m', 0); c1 = u.get('cw1h', 0)
    return (u.get('in', 0) * pin + u.get('out', 0) * pout + c5 * pin * 1.25 + c1 * pin * 2
            + u.get('cr', 0) * pread) / 1e6 + u.get('web', 0) * WEB_SEARCH_USD


def load(files):
    """Події: assistant (usage, інструменти), user (запит QA / відмова інструмента)."""
    seen = {}; ev = []
    for f in files:
        sub = '/subagents/' in f
        sess = os.path.basename(os.path.dirname(os.path.dirname(f))) if sub else os.path.basename(f)[:-6]
        for line in open(f, encoding='utf-8', errors='replace'):
            try:
                d = json.loads(line)
            except Exception:
                continue
            t = d.get('type'); when = ts(d.get('timestamp'))
            if not when:
                continue
            m = d.get('message') or {}
            if t == 'assistant' and m.get('usage'):
                key = (m.get('id'), d.get('requestId'))
                u = m['usage']; cc = u.get('cache_creation') or {}
                rec = {'t': when, 'kind': 'a', 'sess': sess, 'sub': sub, 'model': m.get('model'),
                       'u': {'in': u.get('input_tokens', 0), 'out': u.get('output_tokens', 0),
                             'cr': u.get('cache_read_input_tokens', 0),
                             'cw5m': cc.get('ephemeral_5m_input_tokens', 0) if cc else u.get('cache_creation_input_tokens', 0),
                             'cw1h': cc.get('ephemeral_1h_input_tokens', 0),
                             'web': (u.get('server_tool_use') or {}).get('web_search_requests', 0)},
                       'tools': [], 'text': ''}
                for b in m.get('content') or []:
                    if b.get('type') == 'tool_use':
                        inp = b.get('input') or {}
                        rec['tools'].append(b.get('name'))
                        rec['text'] += json.dumps(inp, ensure_ascii=False)[:4000]
                        if b.get('name') == 'Skill':
                            rec.setdefault('skills', []).append(inp.get('skill'))
                if key in seen:  # одне повідомлення пишеться кількома рядками — usage однаковий
                    old = seen[key]; old['tools'] += rec['tools']; old['text'] += rec['text']
                    old.setdefault('skills', []).extend(rec.get('skills', []))
                    continue
                seen[key] = rec; ev.append(rec)
            elif t == 'user' and not sub:
                c = m.get('content')
                if isinstance(c, str) and c.startswith('This session is being continued'):
                    continue
                if isinstance(c, str):
                    cmd = re.search(r'<command-name>/?([\w:-]+)</command-name>', c)
                    ev.append({'t': when, 'kind': 'u', 'sess': sess, 'text': c[:4000],
                               'cmd': cmd.group(1) if cmd else None})
                elif isinstance(c, list):
                    for b in c:
                        if b.get('type') == 'tool_result' and 'doesn\'t want to proceed' in json.dumps(b.get('content'), ensure_ascii=False):
                            ev.append({'t': when, 'kind': 'r', 'sess': sess})
                        elif b.get('type') == 'text' and not str(b.get('text', '')).startswith('<'):
                            ev.append({'t': when, 'kind': 'u', 'sess': sess, 'text': b.get('text', '')[:4000], 'cmd': None})
    ev.sort(key=lambda e: e['t'])
    return ev


def all_files():
    return glob.glob(f'{PROJECTS}/*/*.jsonl') + glob.glob(f'{PROJECTS}/*/*/subagents/*.jsonl')


def agg(events):
    u = defaultdict(int); usd = 0.0; tools = defaultdict(int); n = 0; sub_usd = 0.0
    for e in events:
        if e['kind'] != 'a':
            continue
        n += 1; c = cost(e['u'], e['model']); usd += c
        if e['sub']:
            sub_usd += c
        for k, v in e['u'].items():
            u[k] += v
        for tl in e['tools']:
            tools[tl] += 1
    return {'u': dict(u), 'usd': usd, 'sub_usd': sub_usd, 'calls': n, 'tools': dict(tools),
            'prompts': sum(1 for e in events if e['kind'] == 'u'),
            'rejects': sum(1 for e in events if e['kind'] == 'r')}


def month_usd(until):
    ev = load(all_files()); since = until - timedelta(days=30)
    return sum(cost(e['u'], e['model']) for e in ev if e['kind'] == 'a' and since <= e['t'] <= until)


def fmt_tok(n):
    return f'{n/1e6:.2f} млн' if n >= 1e6 else f'{n/1e3:.1f} тис.'


def fmt_dur(td):
    m = int(td.total_seconds() // 60); return f'{m // 60} год {m % 60:02d} хв' if m >= 60 else f'{m} хв'


def times(events, start, end):
    """Робота агента / очікування QA: паузи перед запитом QA — очікування, решта — робота."""
    main = [e for e in events if not e.get('sub')]
    work = timedelta(); wait = timedelta(); prev = start
    for e in main:
        gap = e['t'] - prev
        if e['kind'] in ('u', 'r'):
            wait += min(gap, WAIT_CAP)
        else:
            work += min(gap, WAIT_CAP)
        prev = e['t']
    return work, wait, end - start


def usage_rows(a, month):
    u = a['u']; tot = sum(u.get(k, 0) for k in ('in', 'out', 'cr', 'cw5m', 'cw1h'))
    share = a['usd'] / month if month else 0
    return [
        ('Викликів моделі', f"{a['calls']}"),
        ('Токени всього', fmt_tok(tot)),
        ('— вхід / вихід', f"{fmt_tok(u.get('in', 0))} / {fmt_tok(u.get('out', 0))}"),
        ('— читання кешу / запис у кеш', f"{fmt_tok(u.get('cr', 0))} / {fmt_tok(u.get('cw5m', 0) + u.get('cw1h', 0))}"),
        ('Еквівалент за цінами API', f"${a['usd']:.2f} (з них субагенти ${a['sub_usd']:.2f})"),
        ('Частка підписки', f"{share*100:.1f} % місячного використання Claude Code → ${share*SUBSCRIPTION_USD:.2f} з ${SUBSCRIPTION_USD:.0f}"),
        ('Запитів QA / відмов інструмента', f"{a['prompts']} / {a['rejects']}"),
    ]


def table(rows, head=('Метрика', 'Значення')):
    out = [f'| {head[0]} | {head[1]} |', '| --- | --- |'] + [f'| {a} | {b} |' for a, b in rows]
    return '\n'.join(out)


def coverage(checklist):
    if not os.path.exists(checklist):
        return ''
    by = defaultdict(lambda: defaultdict(int))
    for l in open(checklist, encoding='utf-8'):
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        if len(c) == 9 and c[0].isdigit():
            by[c[7] or '—'][c[8] or 'не виконано'] += 1
    total = sum(sum(v.values()) for v in by.values())
    rows = ['| Виконання | Рядків | Частка | Pass | Fail | Blocked | Без результату |', '| --- | --- | --- | --- | --- | --- | --- |']
    for k, v in sorted(by.items(), key=lambda x: -sum(x[1].values())):
        n = sum(v.values())
        rows.append(f"| {k} | {n} | {n/total*100:.0f} % | {v.get('Pass', 0)} | {v.get('Fail', 0)} | {v.get('Blocked', 0)} | {v.get('не виконано', 0)} |")
    auto = sum(sum(v.values()) for k, v in by.items() if k in ('агент', 'API', 'автотести'))
    rows.append(f'\nАвтоматизовано (агент + API + автотести): **{auto} з {total} ({auto/total*100:.0f} %)**.')
    return '\n'.join(rows)


def cmd_mark(a):
    os.makedirs(a.run, exist_ok=True)
    with open(os.path.join(a.run, 'marks.jsonl'), 'a', encoding='utf-8') as f:
        f.write(json.dumps({'tc': a.tc, 'event': a.event, 'ts': datetime.now(timezone.utc).isoformat(), 'note': a.note}, ensure_ascii=False) + '\n')
    print('mark', a.tc, a.event)


def cmd_run(a):
    marks = [json.loads(l) for l in open(os.path.join(a.run, 'marks.jsonl'), encoding='utf-8')]
    ev = load(all_files())
    start = min(ts(m['ts']) for m in marks); end = max(ts(m['ts']) for m in marks)
    win = [e for e in ev if start <= e['t'] <= end]
    month = month_usd(end)
    lines = [f'# Метрики прогону {os.path.basename(a.run.rstrip("/"))}', '',
             f'Період: {start.astimezone():%Y-%m-%d %H:%M} — {end.astimezone():%H:%M}. Згенеровано `metrics.py run`.', '']
    work, wait, wall = times(win, start, end)
    tot = agg(win)
    lines += ['## Разом', '', table([('Тривалість', fmt_dur(wall)), ('— робота агента', fmt_dur(work)),
                                    ('— очікування QA', fmt_dur(wait))] + usage_rows(tot, month)), '']
    lines += ['## По кейсах', '', '| TC | Тривалість | Робота агента | Очікування QA | Викликів | Токени | $ API | Інструментів | Нотатка |',
              '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    open_ = {}
    for m in marks:
        if m['event'] == 'start':
            open_[m['tc']] = m
        elif m['event'] == 'end' and m['tc'] in open_:
            s, e = ts(open_[m['tc']]['ts']), ts(m['ts'])
            w = [x for x in ev if s <= x['t'] <= e]; g = agg(w); wk, wt, wl = times(w, s, e)
            toks = sum(g['u'].get(k, 0) for k in ('in', 'out', 'cr', 'cw5m', 'cw1h'))
            lines.append(f"| {m['tc']} | {fmt_dur(wl)} | {fmt_dur(wk)} | {fmt_dur(wt)} | {g['calls']} | {fmt_tok(toks)} | ${g['usd']:.2f} | {sum(g['tools'].values())} | {m.get('note') or open_[m['tc']].get('note') or ''} |")
    lines += ['', '## Інструменти', '', table(sorted(((k, str(v)) for k, v in tot['tools'].items()), key=lambda x: -int(x[1])), ('Інструмент', 'Викликів')), '']
    if a.task:
        lines += ['## Покриття чек-листа', '', coverage(f'work/{a.task}/03-checklist.md'), '']
    out = os.path.join(a.run, 'metrics.md'); open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n'); print(out)


def stage_of(seg_text, skills, cmd, current):
    for s in tuple(reversed(skills)) + (cmd,):  # останній викликаний скіл qa-* у відрізку
        if s and s.startswith('qa-'):
            return s
    return current


def cmd_task(a):
    files = [f for f in all_files() if '/subagents/' not in f]
    tag = f'work/{a.task}'
    sess_files = [f for f in files if a.task in open(f, encoding='utf-8', errors='replace').read()]
    sess_ids = {os.path.basename(f)[:-6] for f in sess_files}
    sub_files = [f for f in all_files() if '/subagents/' in f and f.split('/')[-3] in sess_ids]
    ev = load(sess_files + sub_files)
    # Відрізки: від запиту QA до наступного запиту QA (у межах сесії).
    segs = []; cur = None
    for e in ev:
        if e['kind'] == 'u' and not e.get('sub'):
            cur = {'start': e['t'], 'sess': e['sess'], 'ev': [e], 'text': e['text'], 'cmd': e.get('cmd'), 'skills': []}
            segs.append(cur)
        elif cur is not None:
            cur['ev'].append(e); cur['text'] += e.get('text', '')
            cur['skills'] += e.get('skills', []) or []
    # Задача «липка» в межах сесії: відрізок без згадки іншої задачі належить останній згаданій.
    stage = {}; task = {}; mine = []
    for s in segs:
        ids = set(re.findall(r'work/(\w[\w-]*)/', s['text']))
        if s['text'].count(a.task) or a.task in ids:
            task[s['sess']] = a.task
        elif ids:
            task[s['sess']] = sorted(ids)[0]
        if task.get(s['sess']) == a.task:
            stage[s['sess']] = stage_of(s['text'], s['skills'], s['cmd'], stage.get(s['sess'], 'інше'))
            s['stage'] = stage[s['sess']]; mine.append(s)
    if not mine:
        print('немає відрізків для задачі'); return
    month = month_usd(mine[-1]['ev'][-1]['t'])
    by = defaultdict(list)
    for s in mine:
        by[s['stage']].append(s)
    lines = [f'# Метрики задачі {a.task}', '', f'Згенеровано `metrics.py task` {datetime.now():%Y-%m-%d %H:%M}. Відрізок = запит QA → наступний запит QA; належить задачі, якщо згадує `{tag}` або {a.task}. Етап — за останнім викликаним скілом qa-*.', '',
             '| Етап (скіл) | Відрізків | Робота агента | Викликів моделі | Токени | $ API | Запитів QA | Відмов |', '| --- | --- | --- | --- | --- | --- | --- | --- |']
    allev = []
    for st, ss in by.items():
        evs = [e for s in ss for e in s['ev']]; allev += evs; g = agg(evs)
        work = sum(((s['ev'][-1]['t'] - s['start']) for s in ss), timedelta())
        toks = sum(g['u'].get(k, 0) for k in ('in', 'out', 'cr', 'cw5m', 'cw1h'))
        lines.append(f"| {st} | {len(ss)} | {fmt_dur(work)} | {g['calls']} | {fmt_tok(toks)} | ${g['usd']:.2f} | {g['prompts']} | {g['rejects']} |")
    tot = agg(allev); work = sum(((s['ev'][-1]['t'] - s['start']) for s in mine), timedelta())
    days = sorted({s['start'].astimezone().date() for s in mine})
    lines += ['', '## Разом', '', table([('Дні роботи', ', '.join(str(d) for d in days)), ('Робота агента (сума відрізків)', fmt_dur(work)), ('Сесій', str(len({s["sess"] for s in mine})))] + usage_rows(tot, month)), '']
    lines += ['## Покриття чек-листа', '', coverage(f'work/{a.task}/03-checklist.md'), '']
    out = f'work/{a.task}/metrics.md'; open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n'); print(out)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); sp = p.add_subparsers(dest='cmd', required=True)
    m = sp.add_parser('mark'); m.add_argument('--run', required=True); m.add_argument('--tc', required=True)
    m.add_argument('--event', choices=['start', 'end'], required=True); m.add_argument('--note', default='')
    r = sp.add_parser('run'); r.add_argument('--run', required=True); r.add_argument('--task')
    t = sp.add_parser('task'); t.add_argument('--task', required=True)
    a = p.parse_args(); {'mark': cmd_mark, 'run': cmd_run, 'task': cmd_task}[a.cmd](a)
