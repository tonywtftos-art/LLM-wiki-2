# 說到還是做到？企業永續作為 LLM Wiki

用 Karpathy 的 **LLM Wiki** 做法整理 7 篇學術文獻，主題是企業的永續作為哪些是**象徵**（symbolic，說到），哪些是**實質**（substantive，做到）。再用這本 wiki 當知識來源，產生一份給非商管背景同學的**教學 HTML 簡報**。

- **Wiki 網站**：https://tonywtftos-art.github.io/LLM-wiki-2/
- **教學簡報**：https://tonywtftos-art.github.io/LLM-wiki-2/slides/
- **GitHub**：https://github.com/tonywtftos-art/LLM-wiki-2
- **規則**：[AGENTS.md](AGENTS.md)
- **流程圖與反思**：[wiki/workflow.md](wiki/workflow.md)（圖：`assets/workflow.png`）
- **檢查紀錄**：[checks/2026-11-18-run.md](checks/2026-11-18-run.md)
- **需求訪談**：[docs/requirements.md](docs/requirements.md)

## 三層架構

| 層 | 位置 | 誰維護 |
|---|---|---|
| 原始資料 | `raw/papers/`（PDF 有版權，不上傳，只在 `raw/README.md` 列清單） | 使用者 |
| Wiki | `wiki/`：7 篇文獻頁、6 個概念頁、簡報大綱 | AI 撰寫，使用者審閱 |
| 規則 | `AGENTS.md` | 使用者和 AI 一起 |

## 檢查程式

```bash
python tools/check_citations.py   # ① 引文對照 PDF（需要 pdftotext 和本機 PDF）
python tools/check_numbers.py     # ① 數字對照 PDF
python tools/check_slides.py      # ②③④ 簡報對照 wiki
python tools/selftest.py          # ⓪ 檢查程式自我測試
```

## 本機預覽

```bash
python -m http.server 8000
# 開啟 http://localhost:8000
```
