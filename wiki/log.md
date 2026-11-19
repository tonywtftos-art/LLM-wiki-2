---
type: log
title: 工作日誌
updated: 2026-11-19
---

# 工作日誌

> 新的放最上面。格式：`## [日期] 類型 | 標題`。類型：setup、ingest、check、query、slides、lint

## [2026-11-19] slides | 修正出處列和內容重疊
- 使用者回報：有幾頁左下角的出處和內容疊在一起
- 原因：出處列固定貼在投影片底部；原本的截圖檢查只測 1280×800，常見筆電的畫面比較矮，內容就會壓到出處列
- 修正：出處列改成排在內容後面，不會重疊；畫面較矮時自動縮小字距與間距
- 測試 5 種尺寸：1920×1080、1536×730、1366×657 都不用捲動；1280×600 有 1 頁要捲動；手機可捲動；**都沒有重疊**
- 規則：AGENTS.md §5.3 第 5 步改成必須測多種筆電尺寸

## [2026-11-19] slides | 簡報第 2 版
- 依新架構重寫 15 張；檢查②③④⑤ 第 1 輪就通過；人眼修正 3 處；詳見 `checks/2026-11-19-run2.md`

## [2026-11-19] query | 重新規劃大綱（使用者退回）
- 使用者審稿：缺少「為什麼只說不做」、文獻只有一篇完整介紹、缺少總整
- 先補 wiki：新增 [[why-talk-not-walk]]、[[literature-synthesis]]；5 篇文獻頁補引文（檢查① 48/48 通過）
- 規則：AGENTS.md §5.3 加入簡報固定架構；新增檢查⑤
- 大綱改成第 2 版（[[teaching-outline]] 有修訂紀錄）

## [2026-11-18] check | 反思後修改 graph
- 檢查程式本身出錯 3 次 → 新增 ⓪ 自我測試 `tools/selftest.py`，9 種錯全部抓到
- 截圖時人眼發現「沒有出處的概括說法」→ 移到檢查②自動檢查
- 更新 [[workflow]]、AGENTS.md §5

## [2026-11-18] slides | 產生教學簡報（迴圈 B）
- Query：依 wiki 規劃 15 頁大綱，存回 [[teaching-outline]]
- 產生 `slides/index.html`；檢查②③④跑了 4 輪才全部通過；截圖修正手機版
- 詳見 [[checks|檢查紀錄]]

## [2026-11-18] check | 檢查①：引文與數字對照原文
- 引文：40 則全部通過；數字：30 個全部通過
- 過程中發現 3 個問題，詳見 `checks/2026-11-18-ingest.md`

## [2026-11-18] ingest | 第一批 7 篇（批次）
- 使用者一次放入 7 篇，AI 依序逐篇處理（決定：批次給檔、逐篇跑迴圈 A）
- 新增文獻頁：[[hrasky-2012]]、[[donia-tetrault-sirsly-2016]]、[[christmann-taylor-2006]]、[[rodrigue-2013]]、[[walker-wan-2012]]、[[wickert-2016]]、[[iatridis-kesidou-2018]]
- 新增概念頁：[[symbolic-vs-substantive]]、[[decoupling]]、[[legitimacy-theory]]、[[external-pressure-internal-motivation]]、[[measuring]]、[[consequences]]
- 標出的矛盾：Donia 用「動機」定義象徵／實質，其他 6 篇用「行動或實踐」→ 寫在 [[symbolic-vs-substantive]]

## [2026-11-18] setup | 訪談與骨架
- AI 先訪談使用者，整理需求（`docs/requirements.md`），確認後才建檔
- 建立骨架：raw/、wiki/、slides/、checks/、tools/
