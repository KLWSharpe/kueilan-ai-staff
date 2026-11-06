#!/usr/bin/env python3
"""自媒體 AI 員工：掃文案裡常見的壞習慣。只回報，不改字。

用法：python3 text_check.py 文案.txt     或     cat 文案.txt | python3 text_check.py
回報分兩級：
  [要改]  破折號、全形 #、標題黨句型
  [看一下] 集體人稱、模板串接詞、AI 範本句、問句收尾
"""
import re
import sys

HARD = [
    (r"[—–]|──", "破折號：改用句號、逗號、冒號或括號"),
    (r"＃", "全形 ＃ 不會被當成 hashtag，改半形 #"),
    (r"震驚|你絕對不知道|最後一個一定|驚呆|99% 的人", "標題黨句型"),
]
SOFT = [
    (r"(^|[^\w])(我們|大家)(?=[^\w]|$)", "集體人稱：改用「我」和「你」"),
    (r"首先|其次|再者|總之|最後，", "模板串接詞"),
    (r"在這個 ?AI 時代|不可否認|值得注意的是|今天來跟大家分享|這篇一定要收藏|希望對你有幫助|不是.*?而是", "AI 範本句或套路句"),
    (r"[？?]\s*$", "問句收尾：改成判斷、下一步或餘韻"),
]


def main():
    if len(sys.argv) > 1 and sys.argv[1] != "-":
        with open(sys.argv[1], encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = sys.stdin.read()
    hard, soft = 0, 0
    lines = text.split("\n")
    for n, line in enumerate(lines, 1):
        for pat, msg in HARD:
            if re.search(pat, line):
                hard += 1
                print(f"[要改] 第 {n} 行：{msg}｜{line.strip()[:60]}")
        for pat, msg in SOFT:
            if re.search(pat, line):
                soft += 1
                print(f"[看一下] 第 {n} 行：{msg}｜{line.strip()[:60]}")
    print(f"結果：要改 {hard} 處，看一下 {soft} 處")
    sys.exit(1 if hard else 0)


if __name__ == "__main__":
    main()
