# 自媒體 AI 員工 變更紀錄

## 0.2.0（2026-11-06）

主打 Codex（ChatGPT 帳號）。README 以「給 Codex 的安裝步驟」為主要裝法並放最前面，Claude Code 裝法移到後面；加入 OpenAI 官方格式的 `.agents/plugins/marketplace.json` 與 `.codex-plugin/plugin.json`；plugin 描述、指令清單與 my-brand 改成 `$指令名` 寫法並括號註明 Claude 寫法。功能與 13 個 skill 不變。

## 0.1.2（2026-11-06）

正文頁與清單頁內容較短時，往下移多一點，整張不再上重下輕。

## 0.1.1（2026-11-06）

寫字規則裡定義禁字的那一行不再出現破折號字元本身，改用文字描述。功能不變。

## 0.1.0（2026-11-06）

第一版。13 個指令：`my-brand`、`make-carousel`、`schedule-post`、`comment-gift` 為完整流程；其餘九個為精簡版（會回應、說明需要的輸入、做基本版本）。

- 做圖用 `scripts/render_carousel.py`（Python 與 Pillow），五種頁型，自動找繁體字型，文字放不下會自動縮字級並回報。
- `scripts/check_tools.sh` 在做圖、剪片前列出缺的工具與安裝方式，缺工具不中斷。
- `scripts/text_check.py` 掃破折號、標題黨、集體人稱等。
- 排程與留言送禮的流程從奎嵐自用的 Meta 排程與 ManyChat 手冊濃縮而來，去掉私人帳號設定，改由品牌設定檔與當次指令決定。
