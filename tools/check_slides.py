"""檢查②③④：簡報對照 wiki。

用法（在專案根目錄）：python tools/check_slides.py
  ② 追溯：大綱每頁都有 wiki 出處；每張投影片都有 data-src，而且指向存在的 wiki 頁；
          投影片中的英文引文（<q> 或 <blockquote>）和數字，必須出現在它引用的 wiki 頁裡。
  ③ 白話：術語第一次出現的那張投影片要用 <dfn> 解釋；中文句子不超過 MAX_LEN 字。
  ④ 矛盾：至少一張 data-role="contradiction" 的投影片，提到 Donia 和至少 3 種判斷依據。
  ⑤ 架構：data-role 順序為 cover → terms → motive → paper… → synthesis → consensus → contradiction → quiz → recap；
          wiki/sources/ 每一篇都有一張 data-paper 投影片，而且有 4 個固定欄位（2026-11-19 使用者審稿後新增）。
有 FAIL 時結束代碼為 1（迴圈 B 的退回邊）。
"""
import re, sys, pathlib, unicodedata
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_LEN = 45
GLOSSARY = ["象徵", "實質", "合法性", "脫鉤", "漂綠", "ISO", "稽核", "CSR", "ROA", "PDCA", "利害關係人"]
BASES = ["文字", "日常", "結果", "動機"]
# 沒有出處的概括說法（第一次執行時，在截圖檢查才被人眼發現，之後移到這裡自動檢查）
ORDER = ["cover", "terms", "motive", "paper", "synthesis", "consensus", "contradiction", "quiz", "recap"]
PAPER_FIELDS = ["研究問題", "怎麼研究", "怎麼分", "發現"]
VAGUE = ["多數人", "大部分人", "大家都", "一般認為", "研究顯示", "普遍認為", "眾所皆知"]

def norm(s):
    s = unicodedata.normalize("NFKC", s).replace("’", "'").replace("–", "-")
    return re.sub(r"[^a-z0-9%]+", " ", s.lower()).strip()

def wiki_pages():
    pages = {}
    for p in (ROOT / "wiki").rglob("*.md"):
        t = p.read_text(encoding="utf-8")
        pages[p.stem] = t; pages[str(p.relative_to(ROOT / "wiki").with_suffix(""))] = t
    return pages

class Slides(HTMLParser):
    def __init__(self):
        super().__init__(); self.slides = []; self.cur = None; self.stack = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section" and "slide" in (a.get("class") or ""):
            self.cur = {"id": a.get("id", f"s{len(self.slides)+1}"), "src": a.get("data-src", ""),
                        "check": a.get("data-check", ""), "role": a.get("data-role", ""), "paper": a.get("data-paper", ""), "text": "", "quotes": [], "dfn": [], "notes": False}
            self.slides.append(self.cur)
        if self.cur is not None:
            self.stack.append(tag)
            if tag in ("q", "blockquote"): self.cur["quotes"].append("")
            if tag == "dfn": self.cur["dfn"].append("")
            if tag == "aside" and "notes" in (a.get("class") or ""): self.cur["notes"] = True
    def handle_endtag(self, tag):
        if self.cur is None: return
        if self.stack: self.stack.pop()
        if tag == "section": self.cur = None
    def handle_data(self, d):
        if self.cur is None: return
        if "script" in self.stack or "style" in self.stack: return
        self.cur["text"] += d + "\n"
        if "q" in self.stack or "blockquote" in self.stack: self.cur["quotes"][-1] += d
        if "dfn" in self.stack: self.cur["dfn"][-1] += d

def main():
    pages = wiki_pages(); fails = []; notes = []
    # ② 大綱
    outline = pages.get("syntheses/teaching-outline", "")
    for row in re.findall(r"^\| (\d+) \|.*$", outline, re.M):
        line = re.search(rf"^\| {row} \|.*$", outline, re.M).group(0)
        links = re.findall(r"\[\[([^\]|]+)", line)
        if not links: fails.append(f"② 大綱第 {row} 頁沒有出處")
        for l in links:
            if l not in pages: fails.append(f"② 大綱第 {row} 頁的出處 [[{l}]] 不存在")
    # ② ③ ④ 簡報
    html = (ROOT / "slides" / "index.html").read_text(encoding="utf-8")
    p = Slides(); p.feed(html); slides = p.slides
    seen = set()
    for i, s in enumerate(slides, 1):
        tag = f"第 {i} 張（{s['id']}）"
        srcs = [x.strip() for x in s["src"].split(",") if x.strip()]
        if not srcs: fails.append(f"② {tag} 沒有 data-src")
        for x in srcs:
            if x not in pages: fails.append(f"② {tag} data-src「{x}」不是 wiki 頁")
        raw = " ".join(pages.get(x, "") for x in srcs)
        corpus = norm(raw)
        rawnum = raw.replace(",", "")          # 數字比對用原文（norm 會把 9.2 變成 9 2）
        for q in s["quotes"]:
            if re.search(r"[A-Za-z]{4,}", q) and norm(q) not in corpus:
                fails.append(f"② {tag} 引文不在出處頁：{q.strip()[:60]}")
        body = re.sub(r"\s+", " ", s["text"])
        for n in set(re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?%?", body)):
            k = n.replace(",", "")
            if len(k.rstrip('%')) < 2 and "." not in k: continue
            if re.fullmatch(r"(19|20)\d\d", k): continue
            if k in (str(i), "14001", "9000"): continue
            if not re.search(rf"(?<!\d){re.escape(k.rstrip('%'))}(?!\d)", rawnum):
                fails.append(f"② {tag} 數字 {n} 不在出處頁")
        # ③ 術語
        for term in GLOSSARY:
            if term in body and term not in seen:
                seen.add(term)
                if not any(term in d for d in s["dfn"]):
                    fails.append(f"③ {tag} 第一次出現「{term}」，但沒有 <dfn> 白話解釋")
        # ③ 句長（去掉英文引文）
        plain = body
        for q in s["quotes"]: plain = plain.replace(re.sub(r"\s+", " ", q), " ")
        for sent in re.split(r"[。！？\n]|(?<=[：；])", s["text"]):
            sent = sent.strip()
            zh = len(re.findall(r"[一-鿿]", sent))
            if zh > MAX_LEN and not re.search(r"[A-Za-z]{6,}.*[A-Za-z]{6,}", sent):
                fails.append(f"③ {tag} 句子太長（{zh} 字）：{sent[:30]}…")
        # ② 概括說法要有出處
        for sent in re.split(r"[。！？\n]", s["text"]):
            for v in VAGUE:
                if v in sent and "〔" not in sent:
                    fails.append(f"② {tag} 「{v}」是沒有出處的概括說法：{sent.strip()[:30]}…")
    # ④ 矛盾
    con = [s for s in slides if s["role"] == "contradiction" or s["check"] == "contradiction"]
    if not con:
        fails.append("④ 沒有說明文獻矛盾的投影片（data-role=\"contradiction\"）")
    for s in con:
        hit = [b for b in BASES if b in s["text"]]
        if "Donia" not in s["text"] or len(hit) < 3:
            fails.append(f"④ 矛盾投影片只提到 {hit}，或沒有提到 Donia")
    # ⑤ 架構
    roles = [s["role"] for s in slides]
    for i, (s, r) in enumerate(zip(slides, roles), 1):
        if r not in ORDER: fails.append(f"⑤ 第 {i} 張沒有合法的 data-role（目前是「{r}」）")
    idx = [ORDER.index(r) for r in roles if r in ORDER]
    if idx != sorted(idx): fails.append(f"⑤ 投影片順序不對：{' → '.join(dict.fromkeys(roles))}")
    for r in ORDER:
        if r not in roles: fails.append(f"⑤ 缺少 {r} 投影片")
    papers = [s for s in slides if s["role"] == "paper"]
    want = sorted(p.stem for p in (ROOT / "wiki" / "sources").glob("*.md"))
    have = [s["paper"] for s in papers]
    for w in want:
        if have.count(w) != 1: fails.append(f"⑤ 文獻 {w} 應該有 1 張自己的投影片，目前 {have.count(w)} 張")
    for s in papers:
        miss = [f for f in PAPER_FIELDS if f not in s["text"]]
        if miss: fails.append(f"⑤ 文獻投影片 {s['paper'] or s['id']} 缺少欄位：{'、'.join(miss)}")
        if s["paper"] and f"sources/{s['paper']}" not in s["src"]:
            fails.append(f"⑤ 文獻投影片 {s['paper']} 的 data-src 沒有指向自己的文獻頁")
    n = len(slides)
    limit = max(15, len(want) + 8)
    if not 12 <= n <= limit: fails.append(f"需求：簡報應有 12–{limit} 頁，目前 {n} 頁")
    print(f"投影片 {n} 張；FAIL {len(fails)}")
    for f in fails: print("- FAIL", f)
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
