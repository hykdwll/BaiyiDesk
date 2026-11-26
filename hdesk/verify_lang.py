#!/usr/bin/env python3
"""校验语言文件替换：元组数量不变、key 不变、value 仅 RustDesk->HDesk。"""
import re
import subprocess
import sys

PAIR = re.compile(r'\("((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\)')

files = sys.argv[1:] or ["cn.rs", "ro.rs", "ar.rs", "ru.rs", "tw.rs", "ja.rs"]
allok = True

for f in files:
    old = subprocess.run(
        ["git", "show", f"HEAD:src/lang/{f}"],
        capture_output=True, text=True, encoding="utf-8",
    ).stdout
    new = open(f"src/lang/{f}", encoding="utf-8").read()

    om, nm = PAIR.findall(old), PAIR.findall(new)
    if len(om) != len(nm):
        print(f"{f}: !! 元组数量 {len(om)} -> {len(nm)}（结构被破坏）")
        allok = False
        continue

    key_changed = sum(1 for (a, _), (b, _) in zip(om, nm) if a != b)
    val_changed = sum(1 for (_, a), (_, b) in zip(om, nm) if a != b)
    val_bad = sum(
        1 for (_, a), (_, b) in zip(om, nm) if b != a.replace("RustDesk", "HDesk")
    )
    cr = open(f"src/lang/{f}", "rb").read().count(b"\r")

    flag = "OK" if (key_changed == 0 and val_bad == 0 and cr == 0) else "!!"
    if flag == "!!":
        allok = False
    print(
        f"{f:10s} {flag}  元组={len(om):4d} key被改={key_changed} "
        f"value被改={val_changed} value非预期={val_bad} CR={cr}"
    )

print("\n全部通过" if allok else "\n存在问题")
