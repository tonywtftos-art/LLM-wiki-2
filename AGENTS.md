# AGENTS.md：永續作為「說到 vs 做到」LLM Wiki 的工作規則

> 給 AI 代理（Claude Code、Codex、Antigravity 等）的說明書。開始任何工作前先讀完這份文件。
> 規則由使用者和 AI 一起維護；要改規則，先問使用者。需求來源：`docs/requirements.md`（訪談紀錄）。

---

## 1. 專案目的與使用者

- **主題**：企業的永續作為，哪些是「說到」（象徵 symbolic），哪些是「做到」（實質 substantive）。
- **兩個產出**：
  1. 一本 LLM Wiki：整理使用者提供的文獻（目前 7 篇）。
  2. 一份教學 HTML 簡報：12–15 頁，含小測驗，**對象是非商管背景的修課同學**。
- **使用者**：政大企研所學生，商管背景。要求查證嚴格，喜歡白話解釋。
- **分工**：使用者負責挑文獻、審稿、決定方向；AI 負責閱讀、整理、交叉連結、檢查、產生簡報。

## 2. 三層架構與資料夾

```
├── AGENTS.md / CLAUDE.md   規則（CLAUDE.md 只指向本檔）
├── docs/requirements.md    需求訪談紀錄
├── raw/papers/             原文 PDF（AI 只讀不改；.gitignore 擋掉，不上傳 GitHub）
├── wiki/
│   ├── index.md            總目錄（也是網站選單的來源）
│   ├── log.md              工作日誌
│   ├── overview.md         專案全貌
│   ├── workflow.md         loop / graph 說明
│   ├── sources/            文獻頁，一篇一頁
│   ├── concepts/           概念頁，跨文獻整合
│   └── syntheses/          Query 的好答案存回來（例如簡報大綱）
├── slides/index.html       教學簡報
├── checks/                 每次執行的檢查報告
├── tools/                  檢查程式（check_citations / check_numbers / check_slides / selftest）
├── index.html + assets/    wiki 網站
```

- 檔名一律英文小寫加連字號，例如 `walker-wan-2012.md`。
- 文獻頁命名：`第一作者-年份`；兩位作者寫 `作者1-作者2-年份`；三位以上寫 `第一作者-年份`。

## 3. 頁面格式

### 3.1 文獻頁（wiki/sources/）

frontmatter 必填：

```yaml
type: source
title: 作者 (年份) 期刊縮寫
authors: 全部作者，用分號分隔
year: 正式出版年
journal: 期刊全名, 卷(期), 起–迄頁
source_file: raw/papers/檔名.pdf
page_offset: 期刊頁碼 − PDF 頁碼（給檢查程式換算用）
verification: 全文 / 摘要 / 未讀
updated: YYYY-MM-DD
```

內文固定段落，依序如下：
1. `## 一句話重點`
2. `## 白話版`：給非商管背景的人看，要有例子
3. `## 研究問題與方法`
4. `## 主要發現`
5. `## 怎麼區分象徵 vs 實質`：**這篇的定義或判斷依據**，必寫
6. `## 重要引文`：英文原文加頁碼
7. `## 和其他文獻的關係`：一致、補充或**矛盾**
8. `## 簡報素材`：可以用在簡報的例子、比喻、題目
9. `## 相關頁面`

### 3.2 概念頁（wiki/concepts/）
`## 白話版` → `## 文獻怎麼說`（或整理表格）→ `## 矛盾`（如果有）→ `## 相關頁面`

### 3.3 綜合整理（wiki/syntheses/）
回答使用者問題或規劃簡報時產生的好答案，存成這類頁面。每個重點都要連回 wiki 頁。

## 4. 寫作與查證規則

- 用繁體中文；**先講結論**；術語第一次出現時附英文和白話解釋。
- 每個事實都要附**頁碼**，格式 `(p.233)` 或 `(pp.183–185)`。頁碼一律用**期刊頁碼**，不是 PDF 頁碼。
- 引文用英文原文加上 `"…"`，只引短句。
- 查證標籤：

| 標籤 | 意思 |
|---|---|
| `[全文]` | 已對照 PDF 原文 |
| `[摘要]` | 只讀了摘要 |
| `[未讀]` | 還沒讀 |
| `〔自訂〕` | 本 wiki 自己的整理或判斷，不是文獻原文 |
| `〔自擬比喻〕` | 為了教學自己想的例子 |

- **矛盾要標出來，不要硬合併**：不同文獻的定義或結果不一致時，在概念頁的「矛盾」段落並列寫出，並說明本 wiki 採用哪一個、為什麼（標〔自訂〕）。
- 禁止事項：
  - 不修改 `raw/` 的檔案
  - 不編造引文、頁碼、數字
  - 不把〔自訂〕寫成文獻的結論
  - PDF 不上傳 GitHub

## 5. 操作流程（詳細流程圖見 `wiki/workflow.md`）

### 5.1 Ingest（迴圈 A，每篇跑一次）
使用者可以一次給多篇，但 AI **一篇跑完整個迴圈再換下一篇**，這樣概念頁才能逐篇累積、比較。

1. 讀 PDF：摘要、前言、理論、方法、結果、結論，並記下頁碼對照（`page_offset`）
2. 依 §3.1 寫文獻頁
3. 更新相關概念頁；新的觀點和既有內容衝突時，寫進「矛盾」段落
4. **檢查①**：執行 `python tools/check_citations.py <檔名>` 和 `python tools/check_numbers.py <檔名>`
   - FAIL → 回到步驟 2 修改，再跑一次（**退回邊**）
   - WARN → 人工確認原文，修正後再跑
5. 更新 `wiki/index.md`（沒列進去的頁面不會出現在網站上）
6. 在 `wiki/log.md` 記一筆 `## [日期] ingest | 標題`
7. 全部做完後，使用者事後審閱

### 5.2 Query
1. 先讀 `wiki/index.md` 找相關頁面，再讀頁面內容回答；**不要直接回 PDF 重新讀**，除非 wiki 沒有
2. 回答要附 wiki 頁連結
3. 好的答案存到 `wiki/syntheses/`，加進 index，記進 log

### 5.3 產生簡報（迴圈 B）

**簡報架構（固定順序，2026-11-19 使用者審稿後新增）**
教學簡報要像一份文獻回顧：先講為什麼，再逐篇介紹，最後總整。每張投影片用 `data-role` 標明角色：

| 順序 | data-role | 內容 | 知識來源 |
|---|---|---|---|
| 1 | `cover` | 封面、學習目標 | overview |
| 2 | `terms` | 關鍵名詞（象徵、實質） | concepts/symbolic-vs-substantive |
| 3 | `motive` | **背景與動機：為什麼公司會只說不做** | syntheses/why-talk-not-walk |
| 4… | `paper` | **每篇文獻一張，架構相同**，並加 `data-paper="文獻頁檔名"` | sources/ |
| 接著 | `synthesis` | 把所有文獻串成一條邏輯 | syntheses/literature-synthesis |
| 接著 | `consensus` | 共識 | syntheses/literature-synthesis |
| 接著 | `contradiction` | 矛盾與分歧 | syntheses/literature-synthesis |
| 接著 | `quiz` | 小測驗 | sources/ |
| 最後 | `recap` | 重點回顧 | overview |

文獻投影片的固定欄位：**研究問題**、**怎麼研究**、**怎麼分象徵 vs 實質**、**發現**，加上一句「帶走這一句」。順序依 literature-synthesis 的邏輯鏈排列，不依年份。

**步驟**
1. **Query**：依觀眾（非商管背景）和上面的架構，從 wiki 規劃大綱，存成 `wiki/syntheses/teaching-outline.md`。每頁都要寫出處（wiki 頁）。大綱需要的內容如果 wiki 沒有（例如「為什麼只說不做」），**先回 wiki 補一頁 synthesis**，再寫大綱
2. **檢查②**：大綱每頁都有 wiki 出處，且出處頁面存在
3. 依大綱寫 `slides/index.html`；每張投影片的 `data-src` 屬性寫出它用的 wiki 頁
4. **檢查②～⑤**：執行 `python tools/check_slides.py`
   - ② 追溯：每頁都有 `data-src`，且指向存在的 wiki 頁；引文和數字必須出現在該 wiki 頁；不能有「多數人、研究顯示」這類沒有出處的概括說法
   - ③ 白話：術語表裡的術語第一次出現時，同一頁要有白話解釋；句子不能太長
   - ④ 矛盾：`contradiction` 投影片要提到 Donia 和至少 3 種判斷依據
   - ⑤ 架構：角色順序符合上表；`wiki/sources/` 的每一篇都有自己的 `paper` 投影片；每張 `paper` 投影片都有 4 個固定欄位
   - 不通過 → 改那一頁再跑，最多 3 輪；3 輪還不行就停下來問使用者
5. 用瀏覽器截圖檢查版面：至少要測 1920×1080、1536×730、1366×657（常見筆電，Windows 縮放 125%）和手機。出處列不能和內容重疊，筆電尺寸不能需要捲動（2026-11-19 使用者發現重疊後新增）
6. 寫檢查報告到 `checks/`，記進 log；大綱頁最下面的「修訂紀錄」加一行

### 5.4 檢查程式自我測試（⓪）
改過 `tools/` 裡任何檢查程式，先跑 `python tools/selftest.py`。全部 CAUGHT 才能相信檢查結果；有 MISSED 就先修檢查程式。
原因：第一次執行時，檢查程式本身出了 3 次錯，造成 25 個假警報（見 `checks/2026-11-18-run.md`）。

### 5.5 Lint（定期健康檢查）
找出：互相矛盾的頁面、沒有被任何頁面連到的孤兒頁、提到但沒有自己頁面的概念、缺少頁碼的說法。

### 5.6 log 格式
`## [YYYY-MM-DD] 類型 | 標題`，類型：setup、ingest、check、query、slides、lint

## 6. 網站

- `index.html` 讀 `wiki/index.md` 產生選單，在瀏覽器把 .md 轉成網頁；`[[檔名]]` 會變成連結
- 新增頁面只要兩步：寫 .md，再在 `wiki/index.md` 加一行 `- [[資料夾/檔名|顯示名稱]]｜一行摘要`
- 本機預覽：在專案根目錄執行 `python -m http.server 8000`，開 `http://localhost:8000`
- GitHub Pages：上傳時要有 `.nojekyll`（空檔，網頁上傳會被略過，要在 GitHub 上用 Create new file 建立）
- 簡報在 `slides/index.html`，網站首頁有連結

## 7. 溝通偏好

- 說明要白話，先講結論
- 不確定的地方直接說不確定，不要猜
- 做了什麼決定，記進 log
