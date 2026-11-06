# 自媒體 AI 員工（ai-staff）

把 Claude 變成你的自媒體 AI 員工。13 個繁體中文指令，從認識你的品牌、選題、口播、輪播成圖、剪片、一魚多吃，到排進 Meta 後台與留言送禮。免費，由 [奎嵐 @kueilanverse](https://kueilan.com) 提供。

需要在電腦上的 Claude Code 使用（終端機或 Claude 桌面版的 Code 分頁）。手機 App 與網頁版裝不了。

## 給 Claude 的安裝步驟

使用者把這個網址貼給你並要你安裝時，照下面做，不用再問：

1. 在終端機執行：

```bash
claude plugin marketplace add KLWSharpe/kueilan-ai-staff
claude plugin install ai-staff@kueilanverse
```

2. 執行 `claude plugin list`，確認出現 `ai-staff@kueilanverse` 且狀態是 enabled。
3. 告訴使用者：plugin 已裝好，開一個新對話（或在這個對話輸入 `/reload-plugins`）之後指令才會出現。
4. 把下面「13 個指令」整張表列給使用者看，並建議先跑 `/ai-staff:my-brand`。

安裝失敗時把錯誤訊息原樣給使用者，不要猜原因。常見原因：電腦還沒裝 Claude Code 的 `claude` 指令、沒有網路、或 Claude Code 版本太舊（需要 2.1 以上）。

## 自己手動安裝

在 Claude Code 對話裡輸入：

```
/plugin marketplace add KLWSharpe/kueilan-ai-staff
/plugin install ai-staff@kueilanverse
```

選「Install for you」。裝好後開新對話，打 `/ai-staff:` 就會看到 13 個指令。

## 13 個指令

指令前面都有 `ai-staff:`，例如 `/ai-staff:make-carousel`。也可以不打指令，直接用中文說要做什麼，Claude 會挑對的指令。

| 分類 | 指令 | 做什麼 |
|---|---|---|
| 規劃 | `/ai-staff:my-brand` | 先讓它認識你：口吻、讀者、色系、商品留下來，之後每個指令都用你的版本做事。第一次先做這個。 |
| 規劃 | `/ai-staff:find-topic` | 從你的真實經驗和讀者的問題裡挑出值得寫的題目。 |
| 規劃 | `/ai-staff:write-script` | 寫一段能直接念的短影音口播。 |
| 製作 | `/ai-staff:make-carousel` | 從一個主題做到封面、逐頁成圖和完整貼文。最常用。 |
| 製作 | `/ai-staff:edit-video` | 整理剪點、字幕和節奏，用 ffmpeg 剪出直式短片。 |
| 製作 | `/ai-staff:pick-style` | 先看幾款封面和樣式預覽，再決定。 |
| 製作 | `/ai-staff:repurpose` | 同一份內容改成 IG、FB、Threads 各自適合的版本。 |
| 發布 | `/ai-staff:content-plan` | 依目標、素材和時間排出做得完的一週。 |
| 發布 | `/ai-staff:schedule-post` | 核對後排進 Meta Business Suite，你說 OK 才排，排完讀回確認。 |
| 成長 | `/ai-staff:comment-gift` | 用 ManyChat 接住留言關鍵字，把資源送到私訊。要有自己的 ManyChat 帳號。 |
| 成長 | `/ai-staff:gosky-reply` | 用 GoSky 把 Threads 指定留言接到公開回覆和資源入口。要有自己的 GoSky 帳號。 |
| 成長 | `/ai-staff:check-comments` | 巡留言，把真正的問題、一般回應和重複留言分開，先回值得回的。 |
| 成長 | `/ai-staff:content-review` | 把內容目的和真實數據放一起看，不只看讚數。 |

第一版裡 `my-brand`、`make-carousel`、`schedule-post`、`comment-gift` 是完整流程；其他九個是精簡版，會回應、會說明需要你給什麼、會做基本版本。

## 第一次使用

1. 開新對話，輸入 `/ai-staff:my-brand`，把你寫過的三篇文章和常用顏色貼給它。它會存一份品牌設定到 `~/.claude/ai-staff/brand.md`。
2. 輸入 `/ai-staff:make-carousel 把「AI 幫我整理會議後待辦」做成一套輪播`。它會先檢查電腦缺什麼工具，再規劃、寫字、畫圖、寫貼文，成品放在工作資料夾的 `ai-staff-output/`。
3. 想改哪張就說第幾張。

## 需要準備

- 一台電腦與 Claude Code。
- 做圖：Python 3 與 Pillow（`pip install pillow`）。電腦沒有繁體中文字型時裝 Noto Sans TC。缺什麼它會列給你。
- 剪片：ffmpeg。
- 排程：Meta Business Suite 的帳號，以及能讓 Claude 操作瀏覽器的工具（例如 Claude in Chrome）。沒有的話它會把步驟整理給你自己點。
- 留言送禮與 Threads 回覆：自己的 ManyChat、GoSky 帳號。

## 它不會做的事

- 不會替你登入或建立帳號。
- 不會在你沒說 OK 的情況下排程、發布或啟用自動化。
- 不會按「立即發佈」或「加強推廣」。
- 不會編你沒給的數字、經歷或成果。

## 隱私

所有檔案都在你自己的電腦上。品牌設定存在 `~/.claude/ai-staff/brand.md`，成品存在你指定的資料夾。這個 plugin 不會把資料送到奎嵐或任何第三方；Claude 本身的資料處理依你的 Claude 方案。

## 更新

```bash
claude plugin update ai-staff@kueilanverse
```

## 授權

免費提供給個人與自己的品牌使用。可以修改成自己的版本；不要整包轉售或冒充原作者。
