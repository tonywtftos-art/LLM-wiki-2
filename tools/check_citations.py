"""檢查①：引文與頁碼對照原文。

用法（在專案根目錄執行，需要 pdftotext）：
    python tools/check_citations.py            # 檢查全部文獻頁
    python tools/check_citations.py hrasky-2012

規則：
- 文獻頁中「"英文引文" … (p.X)」的引文，必須出現在 PDF 的第 X 頁（允許前後 1 頁，因為句子可能跨頁）。
- 頁碼換算：期刊頁碼 = PDF 頁碼 + page_offset（寫在 frontmatter）。
- 找不到的引文列為 FAIL，要回去修改文獻頁（迴圈 A 的退回邊）。
"""
import re, subprocess, sys, pathlib, unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    s = re.sub(r"-\s+", "", s)            # 斷行連字號
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return s.strip()

def front(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    d = {}
    for line in (m.group(1) if m else "").splitlines():
        if ":" in line:
            k, v = line.split(":", 1); d[k.strip()] = v.strip()
    return d

def pdf_pages(path):
    out = subprocess.run(["pdftotext", str(path), "-"], capture_output=True, text=True).stdout
    return [norm(p) for p in out.split("\f")]

def check(md):
    text = md.read_text(encoding="utf-8")
    fm = front(text)
    pdf = ROOT / fm["source_file"]; off = int(fm["page_offset"])
    pages = pdf_pages(pdf)
    rows = []
    # 引文後面最近的 (p.X) 或 (pp.X–Y)
    for m in re.finditer(r'"([^"]{25,})"[^"\n]{0,80}?\(pp?\.(\d+)', text):
        quote, pg = m.group(1), int(m.group(2))
        parts = [norm(x) for x in re.split(r"…|\.\.\.|\[[^\]]*\]", quote) if len(norm(x)) > 15]
        idx = pg - off - 1
        window = " ".join(pages[max(0, idx - 1): idx + 2])
        ok = all(p in window for p in parts) if parts else False
        # 頁碼錯但原文存在 → 找出正確頁
        found = None
        if not ok:
            for i, p in enumerate(pages):
                if parts and all(x in p for x in parts):
                    found = i + 1 + off; break
        rows.append((ok, pg, found, quote[:70]))
    # 沒有標頁碼的引文：在整篇 PDF 中找，提醒補上頁碼
    cited = {m.group(1) for m in re.finditer(r'"([^"]{25,})"[^"\n]{0,80}?\(pp?\.(\d+)', text)}
    for m in re.finditer(r'"([^"]{25,})"', text):
        q = m.group(1)
        if q in cited: continue
        parts = [norm(x) for x in re.split(r"…|\.\.\.|\[[^\]]*\]", q) if len(norm(x)) > 15]
        found = next((i + 1 + off for i, p in enumerate(pages) if parts and all(x in p for x in parts)), None)
        rows.append(("nopage", None, found, q[:70]))
    return rows

def main():
    files = sorted((ROOT / "wiki" / "sources").glob("*.md"))
    if len(sys.argv) > 1:
        files = [f for f in files if f.stem in sys.argv[1:]]
    total = bad = 0
    for f in files:
        rows = check(f)
        print(f"\n## {f.stem}（{len(rows)} 則引文）")
        for ok, pg, found, q in rows:
            total += 1
            if ok == "nopage":
                if found:
                    print(f"- NOTE 未標頁碼，原文在 p.{found}｜{q}")
                else:
                    bad += 1
                    print(f"- **FAIL** 未標頁碼且原文找不到｜{q}")
            elif ok:
                print(f"- PASS p.{pg}｜{q}")
            else:
                bad += 1
                hint = f"原文在 p.{found}" if found else "原文找不到"
                print(f"- **FAIL** p.{pg}（{hint}）｜{q}")
    print(f"\n合計：{total} 則，通過 {total - bad}，失敗 {bad}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
