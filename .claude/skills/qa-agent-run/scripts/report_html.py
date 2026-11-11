#!/usr/bin/env python3
"""HTML-звіт прогону: report.md + metrics.md прогону + metrics.md задачі → report.html.

Використання:
  python3 report_html.py work/<ID>/05-runs/<дата>
Результат: work/<ID>/05-runs/<дата>/report.html (один файл, без зовнішніх ресурсів).
"""
import html
import re
import sys
from collections import Counter
from pathlib import Path

STATUS = {
    'PASS': 'pass', 'FAIL': 'fail', 'BLOCKED': 'blocked', 'FLAKY': 'blocked',
    'Pass': 'pass', 'Fail': 'fail', 'Blocked': 'blocked',
}


def inline(t, base):
    t = html.escape(t, quote=False)
    def code(m):
        c = m.group(1)
        if re.fullmatch(r'TC-\d+/[^`\s]+\.(png|pdf|jpg)', html.unescape(c)) and (base / html.unescape(c)).exists():
            return f'<a href="{c}"><code>{c}</code></a>'
        return f'<code>{c}</code>'
    t = re.sub(r'`([^`]+)`', code, t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return t


def status_cell(text):
    if re.fullmatch(r'(CHK|TC|BUG)-\d+', text):
        return ' class="id"'
    for k, cls in STATUS.items():
        if text.startswith(k):
            return f' class="st {cls}"'
    return ''


def md_to_html(md, base, skip_h1=True):
    out, lines, i = [], md.split('\n'), 0
    while i < len(lines):
        l = lines[i]
        if l.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            head, body = rows[0], [r for r in rows[2:]]
            h = ''.join(f'<th>{inline(c, base)}</th>' for c in head) if any(head) else ''
            b = ''.join('<tr>' + ''.join(f'<td{status_cell(c)}>{inline(c, base)}</td>' for c in r) + '</tr>' for r in body)
            out.append(f'<div class="tw"><table>{"<thead><tr>" + h + "</tr></thead>" if h else ""}<tbody>{b}</tbody></table></div>')
            continue
        m = re.match(r'^(#{1,4}) (.*)', l)
        if m:
            n = len(m.group(1))
            if not (n == 1 and skip_h1):
                out.append(f'<h{n + 1}>{inline(m.group(2), base)}</h{n + 1}>')
            i += 1
            continue
        if re.match(r'^(- |\d+\. )', l):
            tag = 'ol' if re.match(r'^\d+\. ', l) else 'ul'
            items = []
            while i < len(lines) and re.match(r'^(- |\d+\. )', lines[i]):
                items.append(re.sub(r'^(- |\d+\. )', '', lines[i]))
                i += 1
            out.append(f'<{tag}>' + ''.join(f'<li>{inline(x, base)}</li>' for x in items) + f'</{tag}>')
            continue
        if l.startswith('> '):
            out.append(f'<p class="note">{inline(l[2:], base)}</p>')
        elif l.strip():
            out.append(f'<p>{inline(l, base)}</p>')
        i += 1
    return '\n'.join(out)


def section(md, title):
    m = re.search(r'^## ' + re.escape(title) + r'.*?$(.*?)(?=^## |\Z)', md, re.M | re.S)
    return m.group(1).strip() if m else ''


def kv(md, title):
    d = {}
    for l in section(md, title).split('\n'):
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        if len(c) == 2 and c[0] not in ('Метрика', '---', ''):
            d[c[0]] = c[1]
    return d


def main():
    run = Path(sys.argv[1])
    task_dir = run.parent.parent
    rep = (run / 'report.md').read_text()
    rmet = (run / 'metrics.md').read_text() if (run / 'metrics.md').exists() else ''
    tmet = (task_dir / 'metrics.md').read_text() if (task_dir / 'metrics.md').exists() else ''
    title = re.search(r'^# (.*)$', rep, re.M).group(1)

    tc = Counter(re.findall(r'^\| TC-\d+ \| ([A-Z]+)', section(rep, 'По кейсах'), re.M))
    chk = Counter(re.findall(r'^\| CHK-\d+ \| TC-\d+ \| ([A-Z]+)', section(rep, 'По перевірках чек-листа'), re.M))
    r, t = kv(rmet, 'Разом'), kv(tmet, 'Разом')
    cov = re.search(r'Автоматизовано[^*]*\*\*([^*]+)\*\*', tmet)
    cov_rows = re.findall(r'^\| (агент|вручну|API|автотести) \| (\d+) \|', tmet, re.M)
    total = sum(int(n) for _, n in cov_rows) or 1

    def card(label, value, sub='', cls=''):
        return f'<div class="card {cls}"><div class="v">{html.escape(value)}</div><div class="l">{html.escape(label)}</div><div class="s">{html.escape(sub)}</div></div>'

    cards = ''.join([
        card('Кейси PASS', str(tc['PASS']), f'з {sum(tc.values())}', 'pass'),
        card('Кейси FAIL', str(tc['FAIL']), (f"зокрема «потребує рішення QA»: {nq}" if (nq := len(re.findall(r'^\| TC-\d+ \| FAIL \(потребує', section(rep, 'По кейсах'), re.M))) else 'усі — баги'), 'fail'),
        card('Кейси BLOCKED', str(tc['BLOCKED'] + tc['FLAKY']), '', 'blocked'),
        card('Перевірки CHK', f"{chk['PASS']} / {chk['FAIL']} / {chk['BLOCKED']}", 'Pass / Fail / Blocked'),
        card('Робота агента (прогін)', r.get('— робота агента', '—'), f"викликів моделі: {r.get('Викликів моделі', '—')}"),
        card('Вартість прогону', r.get('Еквівалент за цінами API', '—').split(' (')[0], r.get('Частка підписки', '').split('→')[-1].strip()),
        card('Вартість задачі', t.get('Еквівалент за цінами API', '—').split(' (')[0], t.get('Частка підписки', '').split('→')[-1].strip()),
        card('Автоматизовано', cov.group(1) if cov else '—', 'агент + API + автотести'),
    ])
    colors = {'агент': '#2e7d32', 'API': '#1565c0', 'автотести': '#6a1b9a', 'вручну': '#9e9e9e'}
    bar = ''.join(f'<span style="width:{int(n) * 100 / total:.1f}%;background:{colors[k]}" title="{k}: {n}">{k} {n}</span>' for k, n in cov_rows)

    head_tbl = md_to_html(re.sub(r'^\*\*Підсумок:\*\*.*$', '', rep.split('\n## ')[0], flags=re.M), run)
    summary = re.search(r'^\*\*Підсумок:\*\*.*$', rep, re.M)
    parts = [f'<p class="summary">{inline(summary.group(0), run)}</p>' if summary else '', head_tbl]
    for name in ['Деталі FAIL, BLOCKED, FLAKY', 'По кейсах', 'По перевірках чек-листа', 'Помічено поза кейсами', 'Метрики', 'Лишилось вручну']:
        body = section(rep, name)
        if body:
            parts.append(f'<h2>{html.escape(name)}</h2>' + md_to_html(body, run))
    if rmet:
        parts.append('<h2>Метрики прогону (детально)</h2>' + md_to_html(re.sub(r'^# .*\n', '', rmet), run))
    if tmet:
        parts.append('<h2>Метрики задачі</h2>' + md_to_html(re.sub(r'^# .*\n', '', tmet), run))

    css = '''body{font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f5f6f8;color:#222}
main{max-width:1200px;margin:0 auto;padding:24px}h1{font-size:24px;margin:0 0 4px}h2{margin-top:36px;border-bottom:2px solid #ddd;padding-bottom:4px}
h3{margin-top:24px}h4{margin-top:18px}.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px;margin:18px 0}
.card{background:#fff;border-radius:8px;padding:12px 14px;box-shadow:0 1px 3px rgba(0,0,0,.08);border-top:4px solid #90a4ae}
.card.pass{border-color:#2e7d32}.card.fail{border-color:#c62828}.card.blocked{border-color:#ef6c00}
.card .v{font-size:22px;font-weight:700}.card .l{font-size:13px;color:#555}.card .s{font-size:12px;color:#888}
.bar{display:flex;height:26px;border-radius:6px;overflow:hidden;margin:6px 0 18px;font-size:12px;color:#fff}
.bar span{display:flex;align-items:center;justify-content:center;white-space:nowrap;overflow:hidden}
.tw{overflow-x:auto}table{border-collapse:collapse;background:#fff;margin:10px 0;width:100%;font-size:13px}
th,td{border:1px solid #e0e0e0;padding:6px 8px;text-align:left;vertical-align:top}th{background:#eceff1}
td.st{font-weight:600}td.id{white-space:nowrap}td.pass{color:#2e7d32;background:#e8f5e9}td.fail{color:#c62828;background:#ffebee}td.blocked{color:#ef6c00;background:#fff3e0}
code{background:#eef1f4;padding:1px 4px;border-radius:3px;font-size:12px}.summary{background:#fff;border-left:4px solid #1565c0;padding:12px 14px;border-radius:4px}
.note{color:#666;font-style:italic}a{color:#1565c0}'''
    doc = f'''<!DOCTYPE html>
<html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{css}</style></head>
<body><main>
<h1>{html.escape(title)}</h1>
<div class="cards">{cards}</div>
<div><strong>Покриття чек-листа ({total} перевірок)</strong></div><div class="bar">{bar}</div>
{''.join(parts)}
</main></body></html>'''
    out = run / 'report.html'
    out.write_text(doc)
    print(out)


if __name__ == '__main__':
    main()
