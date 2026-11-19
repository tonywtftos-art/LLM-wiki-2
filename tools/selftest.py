"""檢查程式的自我測試：故意放錯，確認檢查程式抓得到。

第一次執行時，檢查程式本身出了 3 次錯（見 checks/2026-11-18-run.md）。
所以規則改成：改過 tools/ 的程式，先跑這支，全部 CAUGHT 才能信任檢查結果。
用法：python tools/selftest.py
"""
import shutil, subprocess, sys, tempfile, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

def run(tmp, script, *args):
    r = subprocess.run([sys.executable, str(tmp / "tools" / script), *args], capture_output=True, text=True, cwd=tmp)
    return r.stdout

def mutate(tmp, rel, old, new):
    p = tmp / rel; t = p.read_text(encoding="utf-8")
    assert old in t, f"找不到要替換的文字：{old[:30]}"
    p.write_text(t.replace(old, new, 1), encoding="utf-8")

CASES = [
    ("假引文", "check_citations.py", "wiki/sources/hrasky-2012.md", "(p.180)\n", '(p.180)\n- "disclosures are always fully substantive in every firm" (p.183)\n', "FAIL"),
    ("頁碼錯", "check_citations.py", "wiki/sources/rodrigue-2013.md", "envisioned as a form of impression management\" (p.111)", "envisioned as a form of impression management\" (p.118)", "FAIL"),
    ("數字錯", "check_numbers.py", "wiki/sources/walker-wan-2012.md", "最後 103 家", "最後 130 家：", "WARN"),
    ("簡報假數字", "check_slides.py", "slides/index.html", "219 筆資料", "412 筆資料", "數字 412"),
    ("簡報假引文", "check_slides.py", "slides/index.html", "<q>you can sleep soundly</q>", "<q>you can always sleep soundly because performance improved</q>", "引文不在出處頁"),
    ("術語沒解釋", "check_slides.py", "slides/index.html", "<p><dfn>合法性</dfn>", "<p>合法性", "合法性"),
    ("句子太長", "check_slides.py", "slides/index.html", "<p class=\"take\">帶走這一句：只看報告書", "<p class=\"take\">帶走這一句：因為它清楚地交代了公司在什麼時間什麼地點用什麼設備達成多少節能成果讓讀者可以自己去查證而且還附上比較基準年。只看報告書", "句子太長"),
    ("沒有出處的概括", "check_slides.py", "slides/index.html", "<p class=\"take\">帶走這一句：只看報告書", "<p class=\"take\">多數人都同意這點。帶走這一句：只看報告書", "概括說法"),
    ("拿掉矛盾頁", "check_slides.py", "slides/index.html", ' data-role="contradiction"', ' data-role="recap"', "④"),
    ("少一篇文獻頁", "check_slides.py", "slides/index.html", 'data-paper="rodrigue-2013"', 'data-paper=""', "rodrigue-2013 應該有 1 張"),
    ("文獻頁缺欄位", "check_slides.py", "slides/index.html", "<b>研究問題</b>", "<b>問題</b>", "缺少欄位"),
    ("順序錯（動機放到最後）", "check_slides.py", "slides/index.html", 'data-role="motive"', 'data-role="recap"', "⑤"),
]

def main():
    ok = True
    for name, script, rel, old, new, expect in CASES:
        with tempfile.TemporaryDirectory() as d:
            tmp = pathlib.Path(d) / "w"
            shutil.copytree(ROOT, tmp, ignore=shutil.ignore_patterns(".git"))
            mutate(tmp, rel, old, new)
            out = run(tmp, script)
            hit = expect in out
            ok &= hit
            print(f"- {'CAUGHT' if hit else '**MISSED**'}｜{name}（{script}）")
    print("\n自我測試：" + ("全部抓到" if ok else "有漏抓，先修檢查程式"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
