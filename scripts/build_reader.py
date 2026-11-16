#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 06_正文_三章.md 与 09_设定附录.md 装配进单文件阅读版 11_阅读版.html"""
import json, re, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / "novel"

def inline(s):
    s = html.escape(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'`(.+?)`', r'<code>\1</code>', s)
    return s

def md_table(lines):
    rows = []
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip('|').split('|')]
        if all(re.fullmatch(r'-{2,}:?|:?-{2,}:?', c) for c in cells if c):
            continue
        rows.append(cells)
    if not rows:
        return ''
    head = ''.join(f'<th>{inline(c)}</th>' for c in rows[0])
    body = ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in rows[1:])
    return f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'

def md_to_html(md):
    out, i = [], 0
    lines = md.split('\n')
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith('|'):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                tbl.append(lines[i]); i += 1
            out.append(md_table(tbl))
            continue
        if re.match(r'^#{1,4} ', ln):
            level = len(ln) - len(ln.lstrip('#'))
            out.append(f'<h{level}>{inline(ln.lstrip("# ").strip())}</h{level}>')
        elif ln.strip() == '---':
            out.append('<hr>')
        elif ln.strip():
            out.append(f'<p>{inline(ln.strip())}</p>')
        i += 1
    return '\n'.join(out)

# ---- 章节 ----
novel_md = (ROOT / '06_正文_三章.md').read_text(encoding='utf-8')
novel_md = novel_md.split('> 风格基线见', 1)[1].split('\n', 1)[1]  # 去掉头部引言
parts = re.split(r'\n## ', '\n' + novel_md)
chapters = []
for p in parts:
    p = p.strip()
    if not p.startswith('第'):
        continue
    title, _, body = p.partition('\n')
    chapters.append({'id': f'ch{len(chapters)+1}', 'title': title.strip(), 'html': md_to_html(body)})

appendix_html = md_to_html((ROOT / '09_设定附录.md').read_text(encoding='utf-8'))
chapters.append({'id': 'appendix', 'title': '设定附录', 'html': appendix_html})

index_data = json.loads((ROOT / '08_索引.json').read_text(encoding='utf-8'))

# 封面：优先图片，失败回退 CSS
cover_block = (
    '<img src="10_封面.png" alt="封面" class="cover-img" '
    'onerror="this.outerHTML=document.getElementById(\'css-cover\').innerHTML">'
    '<div id="css-cover" style="display:none"></div>'
)

css_cover = (ROOT / '10_封面_CSS.html').read_text(encoding='utf-8')
# 提取 .cover 节点作为回退
m = re.search(r'(<div class="cover">.*?</div>\s*</div>\s*</body>)', css_cover, re.S)
css_cover_inner = m.group(1) if m else '<div class="cover" style="background:#ccc;color:#555;display:flex;align-items:center;justify-content:center">账本城</div>'

template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>账本城 · 单文件阅读版</title>
<style>
  :root{--ink:#31383f;--accent:#5d7183;--bg:#f7f5f0;--panel:#efece5;--line:#ddd6c8;}
  *{box-sizing:border-box}
  body{margin:0;font-family:Georgia,"Songti SC","SimSun",serif;color:var(--ink);background:var(--bg)}
  header{position:sticky;top:0;background:var(--panel);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;z-index:5}
  header h1{font-size:18px;margin:0;letter-spacing:.2em}
  #search{flex:1;min-width:200px;padding:7px 12px;border:1px solid var(--line);border-radius:6px;font-size:14px;background:#fff}
  #hits{position:absolute;top:52px;right:16px;background:#fff;border:1px solid var(--line);border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.12);max-height:280px;overflow:auto;width:300px;display:none;z-index:9}
  #hits div{padding:8px 12px;cursor:pointer;font-size:14px;border-bottom:1px solid #f0ece2}
  #hits div:hover{background:var(--panel)}
  #hits b{color:var(--accent)}
  #hits .cat{float:right;color:#9aa0a6;font-size:12px}
  .wrap{display:flex;max-width:1100px;margin:0 auto}
  nav{width:230px;flex-shrink:0;padding:18px 10px;border-right:1px solid var(--line)}
  nav button{display:block;width:100%;text-align:left;padding:10px 14px;margin:4px 0;border:none;background:none;font-size:15px;cursor:pointer;border-radius:6px;font-family:inherit;color:var(--ink)}
  nav button.active{background:var(--accent);color:#fff}
  nav button:hover:not(.active){background:#e7e2d6}
  main{flex:1;padding:26px 34px;max-width:820px}
  .pane{display:none}.pane.active{display:block}
  .pane h2{letter-spacing:.15em;border-bottom:2px solid var(--accent);padding-bottom:8px}
  .pane h3{color:var(--accent);margin-top:28px}
  .pane p{line-height:1.9;font-size:16.5px;margin:10px 0}
  .pane table{border-collapse:collapse;width:100%;margin:14px 0;font-size:14px;background:#fff}
  .pane th,.pane td{border:1px solid var(--line);padding:7px 10px;text-align:left}
  .pane th{background:var(--panel)}
  mark{background:#ffe9a8;padding:0 2px;border-radius:3px}
  .cover-img{max-width:420px;display:block;margin:0 auto;box-shadow:0 10px 30px rgba(0,0,0,.15)}
  .cover-fallback{width:420px;height:630px;margin:0 auto;position:relative;overflow:hidden;background:#cfd9e2;box-shadow:0 10px 30px rgba(0,0,0,.15)}
  .cover-fallback .t{position:absolute;top:100px;width:100%;text-align:center;font-size:52px;letter-spacing:.3em;color:#3a4652}
  .cover-fallback .led{position:absolute;left:46px;right:46px;bottom:40px;height:260px;background:#f2ecdd;border:1px solid #d3c8ab}
  .cover-fallback .pd{position:absolute;left:50%;top:220px;width:3px;height:120px;background:#5d7183;transform-origin:top;transform:rotate(24deg)}
  .cover-fallback .sh{position:absolute;left:170px;top:350px;width:220px;height:8px;background:linear-gradient(90deg,rgba(93,113,131,.45),transparent);transform:rotate(9deg)}
  .cover-fallback .n{position:absolute;bottom:8px;width:100%;text-align:center;font-size:11px;color:#8a94a0}
  footer{color:#9aa0a6;text-align:center;padding:30px;font-size:13px}
</style>
</head>
<body>
<header>
  <h1>账本城</h1>
  <input id="search" type="search" placeholder="检索人物 / 地点 / 道具 / 术语……" autocomplete="off">
</header>
<div id="hits"></div>
<div class="wrap">
  <nav id="toc"></nav>
  <main id="content"></main>
</div>
<footer>《账本城》· AI 参与创作 · 课堂虚构世界观 · 单文件阅读版（零外部依赖）</footer>
<script>
const CHAPTERS = __CHAPTERS__;
const INDEX = __INDEX__;
const CSS_COVER = __CSS_COVER__;

const toc = document.getElementById('toc'), content = document.getElementById('content');
const panes = [];
// 封面页（优先图片，缺图回退 CSS）
const coverPane = document.createElement('section');
coverPane.className = 'pane'; coverPane.id = 'cover';
coverPane.innerHTML = '<img src="10_封面.png" alt="封面" class="cover-img" onerror="this.style.display=\\'none\\';document.getElementById(\\'cover-fb\\').style.display=\\'block\\'">'
  + '<div id="cover-fb" class="cover-fallback" style="display:none"><div class="t">账本城</div><div class="pd"></div><div class="sh"></div>'
  + '<div class="led"></div><div class="n">图像生成未启用 · CSS 构图封面</div></div>';
content.appendChild(coverPane); panes.push(coverPane);
CHAPTERS.forEach((c, idx) => {
  const s = document.createElement('section');
  s.className = 'pane'; s.id = c.id; s.dataset.idx = idx;
  s.innerHTML = c.html;
  content.appendChild(s); panes.push(s);
});
function show(i){
  panes.forEach((p, j) => p.classList.toggle('active', i === j));
  btns.forEach((b, j) => b.classList.toggle('active', i === j));
  window.scrollTo(0, 0);
  clearMarks();
}
const btns = [];
['封面'].concat(CHAPTERS.map(c => c.title)).forEach((t, i) => {
  const b = document.createElement('button');
  b.textContent = t;
  b.onclick = () => show(i);
  toc.appendChild(b); btns.push(b);
});
show(0);

// ---- 索引检索：输入过滤条目，点击高亮并跳转 ----
const input = document.getElementById('search'), hits = document.getElementById('hits');
function clearMarks(){ document.querySelectorAll('mark').forEach(m => { const t = m.textContent; m.replaceWith(t); }); }
input.addEventListener('input', () => {
  const q = input.value.trim().toLowerCase();
  if (!q) { hits.style.display = 'none'; return; }
  const list = INDEX.items.filter(it => it.name.toLowerCase().includes(q) || it.gloss.toLowerCase().includes(q));
  hits.innerHTML = '';
  if (!list.length) { hits.innerHTML = '<div>无匹配条目</div>'; hits.style.display = 'block'; return; }
  list.forEach(it => {
    const d = document.createElement('div');
    d.innerHTML = '<b>' + it.name + '</b><span class="cat">' + it.category + ' · 第' + it.first_chapter + '章</span><br>' + it.gloss;
    d.onclick = () => { jump(it.name); };
    hits.appendChild(d);
  });
  hits.style.display = 'block';
});
function jump(name){
  hits.style.display = 'none';
  clearMarks();
  // 优先在当前章节找，找不到则跳到首次出现的章节
  const cur = panes.findIndex(p => p.classList.contains('active'));
  const order = [cur].concat(panes.map((_, i) => i).filter(i => i !== cur));
  for (const i of order) {
    const pane = panes[i];
    const walker = document.createTreeWalker(pane, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const pos = node.textContent.indexOf(name);
      if (pos >= 0) {
        show(i);
        requestAnimationFrame(() => {
          const after = node.splitText(pos);
          after.splitText(name.length);
          const mark = document.createElement('mark');
          mark.textContent = name;
          node.parentNode.replaceChild(mark, after);
          mark.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
        return;
      }
    }
  }
}
document.addEventListener('click', e => { if (!hits.contains(e.target) && e.target !== input) hits.style.display = 'none'; });
</script>
</body>
</html>
'''

page = template.replace('__CHAPTERS__', json.dumps(chapters, ensure_ascii=False)) \
               .replace('__INDEX__', json.dumps(index_data, ensure_ascii=False)) \
               .replace('__CSS_COVER__', json.dumps(css_cover_inner, ensure_ascii=False))

out = ROOT / '11_阅读版.html'
out.write_text(page, encoding='utf-8')
print('written', out, len(page), 'chars;', len(chapters), 'chapters')
