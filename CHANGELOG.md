# 自媒體 AI 員工 變更紀錄

## 0.1.1（2026-11-06）

寫字規則裡定義禁字的那一行不再出現破折號字元本身，改用文字描述。功能不變。

## 0.1.0（2026-11-06）

第一版。13 個指令：`my-brand`、`make-carousel`、`schedule-post`、`comment-gift` 為完整流程；其餘九個為精簡版（會回應、說明需要的輸入、做基本版本）。

- 做圖用 `scripts/render_carousel.py`（Python 與 Pillow），五種頁型，自動找繁體字型，文字放不下會自動縮字級並回報。
- `scripts/check_tools.sh` 在做圖、剪片前列出缺的工具與安裝方式，缺工具不中斷。
- `scripts/text_check.py` 掃破折號、標題黨、集體人稱等。
- 排程與留言送禮的流程從奎嵐自用的 Meta 排程與 ManyChat 手冊濃縮而來，去掉私人帳號設定，改由品牌設定檔與當次指令決定。
