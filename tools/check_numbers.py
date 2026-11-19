"""檢查①b：數字與頁碼對照原文。

文獻頁中，同一行有頁碼 (p.X) 又有數字的，檢查每個數字是否出現在 PDF 的第 X 頁（允許前後 1 頁）。
找不到的列為 WARN，需要人工確認（可能是換算、中文寫法不同或頁碼錯）。
用法：python tools/check_numbers.py [文獻頁名稱]
"""
import re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from check_citations import ROOT, front, pdf_pages

def numbers(line):
    line = re.sub(r"\(pp?\.[^)]*\)", " ", line)          # 去掉頁碼
    line = re.sub(r'"[^"]*"', " ", line)                  # 引文由 check_citations 檢查
    line = re.sub(r"\b(?:H|P|命題 ?)\d+[a-c]?\b", " ", line)  # 假說／命題編號
    line = re.sub(r"\b(19|20)\d{2}\b", " ", line)          # 年份另行處理
    line = re.sub(r"ISO \d+|SA \d+|1–7|PDCA|CO₂", " ", line)
    return [n.replace(",", "") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", line) if len(n.replace(",", "")) >= 2 or "." in n]

WORDS = {"twenty eight": "28", "twenty two": "22", "ten": "10", "eight": "8", "five": "5", "four": "4",
         "three": "3", "two": "2", "six": "6", "seven": "7", "nine": "9", "eleven": "11", "twelve": "12"}

def main():
    files = sorted((ROOT / "wiki" / "sources").glob("*.md"))
    if len(sys.argv) > 1: files = [f for f in files if f.stem in sys.argv[1:]]
    warn = total = 0
    for f in files:
        text = f.read_text(encoding="utf-8"); fm = front(text)
        off = int(fm["page_offset"]); pages = pdf_pages(ROOT / fm["source_file"])
        body = text.split("---", 2)[2]
        print(f"\n## {f.stem}")
        for line in body.splitlines():
            pg = []
            for grp in re.findall(r"pp?\.([\d,–\- ]+)", line):   # p.233、pp.228, 232、pp.183–185
                for part in grp.split(","):
                    ab = [x for x in re.split(r"[–-]", part.strip()) if x.strip().isdigit()]
                    if ab: pg.append((ab[0], ab[-1] if len(ab) > 1 else ""))
            if not pg: continue
            nums = numbers(line)
            if not nums: continue
            idx = set()
            for a, b in pg:
                a = int(a); b = int(b) if b else a
                for x in range(a, b + 1): idx |= {x - off - 2, x - off - 1, x - off}
            window = " ".join(pages[i] for i in sorted(idx) if 0 <= i < len(pages))
            for w, d in WORDS.items():                       # 原文用英文數字（Ten interviewees）
                window = re.sub(rf"\b{w}\b", d, window)
            for n in nums:
                total += 1
                if re.search(rf"(?<![\d.]){re.escape(n)}(?![\d])", window) or re.search(rf"(?<![\d.]){re.escape(n.replace('.', ' '))}(?![\d])", window):
                    continue
                warn += 1
                print(f"- WARN 數字 {n} 不在所引頁｜{line.strip()[:90]}")
    print(f"\n合計：檢查 {total} 個數字，WARN {warn}")

if __name__ == "__main__":
    main()
