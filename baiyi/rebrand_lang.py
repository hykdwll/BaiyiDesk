#!/usr/bin/env python3
"""把 src/lang/*.rs 里“显示文本”（元组第二个字符串）中的 RustDesk 替换为 BaiyiDesk。

关键约束：
1. 绝不动 key —— 代码用 t!("About RustDesk") 这类 key 查表，key 改了文案就丢了。
2. 不动元组的结尾标点 —— 原先的正则把 `),` 一起吞掉，产生了 `)),` 造成语法错误。
3. 保持 LF 换行 —— Windows 上写文件默认可能引入 CRLF，导致整文件级 diff。
"""
import re
from pathlib import Path

LANG_DIR = Path(__file__).resolve().parent.parent / "src" / "lang"

# 只匹配 ( "key" , "value" )  这两段字符串，结尾括号不纳入捕获
PAIR_RE = re.compile(r'\("((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\)')

total_files = 0
total_hits = 0

for f in sorted(LANG_DIR.glob("*.rs")):
    raw = f.read_bytes()
    src = raw.decode("utf-8")
    if "RustDesk" not in src:
        continue

    hits = [0]

    def sub(m):
        key, val = m.group(1), m.group(2)
        if "RustDesk" in val:
            hits[0] += val.count("RustDesk")
            val = val.replace("RustDesk", "BaiyiDesk")
        return f'("{key}", "{val}")'

    new = PAIR_RE.sub(sub, src)
    if hits[0]:
        f.write_bytes(new.encode("utf-8"))  # 以二进制写入，杜绝 CRLF
        total_files += 1
        total_hits += hits[0]
        print(f"  {f.name:12s} 替换 {hits[0]:3d} 处")

print(f"\n共 {total_files} 个文件, {total_hits} 处显示文本已改为 BaiyiDesk")
