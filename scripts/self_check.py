#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 2 课自检脚本：统计三章字数与对话数、CSV 行列数、JSON 合法性、禁用词检索、伏笔闭合"""
import json, csv, re, sys, io, pathlib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = pathlib.Path(__file__).resolve().parent.parent / "novel"
ok = True

# 1) 三章字数与对话
text = (ROOT / "06_正文_三章.md").read_text(encoding="utf-8")
print("== 三章字数与对话 ==")
for ch in re.split(r"\n## ", text)[1:]:
    title = ch.split("\n")[0]
    body = "\n".join(l for l in ch.split("### 状态登记")[0].split("\n") if not l.startswith("#"))
    cjk = len(re.findall(r"[\u4e00-\u9fff]", body))
    dlg = len(re.findall(r"「[^」]*」", body))
    good = cjk >= 800 and dlg >= 6
    ok &= good
    print(f"  {title}: 汉字={cjk} 对话={dlg}处 {'OK' if good else 'FAIL'}")

# 2) 禁用词
print("== 禁用词 ==")
for w in ["购买", "付款", "价格", "钱", "突然", "竟然", "寄存所"]:
    n = text.count(w)
    ok &= (n == 0)
    print(f"  {w}: {n} {'OK' if n == 0 else 'FAIL'}")

# 3) CSV 行列
print("== CSV 行列 ==")
expect = {"02_人物小传.csv": 4, "03_人物关系矩阵.csv": 4, "04_章节大纲.csv": 9, "05_伏笔回收表.csv": 2}
for f, n in expect.items():
    rows = list(csv.reader(open(ROOT / f, encoding="utf-8")))
    good = len(rows) - 1 == n
    ok &= good
    print(f"  {f}: {len(rows)-1} 数据行 x {len(rows[0])}列 {'OK' if good else 'FAIL'}")

# 4) JSON 与 related 命中
print("== 索引 JSON ==")
j = json.loads((ROOT / "08_索引.json").read_text(encoding="utf-8"))
names = {i["name"] for i in j["items"]}
miss = [r for i in j["items"] for r in i["related"] if r not in names]
notin = [i["name"] for i in j["items"] if i["name"] not in text]
good = not miss and not notin
ok &= good
print(f"  条目={len(j['items'])} related未命中={miss or '无'} 未在正文出现={notin or '无'} {'OK' if good else 'FAIL'}")

# 5) 伏笔闭合
rows = list(csv.reader(open(ROOT / "05_伏笔回收表.csv", encoding="utf-8")))
closed = all(len(r) >= 7 and r[6] == "是" for r in rows[1:])
print(f"== 伏笔闭合 == F1/F2 均闭合: {'OK' if closed else 'FAIL'}")
ok &= closed

print("\n总体:", "全部通过" if ok else "存在未通过项")
sys.exit(0 if ok else 1)
