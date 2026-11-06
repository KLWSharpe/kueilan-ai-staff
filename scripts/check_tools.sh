#!/usr/bin/env bash
# 自媒體 AI 員工：檢查這台電腦上缺哪些工具。
# 用法：bash check_tools.sh [--for carousel|video|all]
# 永遠以 exit 0 結束，缺的工具用清單列出來，不中斷流程。
NEED="${2:-all}"
if [ "$1" = "--for" ]; then NEED="$2"; fi
OK=0; MISS=0; OPT=0
line() { printf '%s\n' "$1"; }
ok()   { OK=$((OK+1));   line "[有]   $1"; }
miss() { MISS=$((MISS+1)); line "[缺]   $1"; }
opt()  { OPT=$((OPT+1));  line "[選配] $1"; }

OS="$(uname -s 2>/dev/null || echo unknown)"
case "$OS" in
  Darwin) HINT_PY="到 https://www.python.org/downloads/ 下載安裝，或 brew install python"; HINT_FF="brew install ffmpeg（沒有 Homebrew 就先到 https://brew.sh 裝）";;
  Linux)  HINT_PY="sudo apt install python3 python3-pip"; HINT_FF="sudo apt install ffmpeg";;
  *)      HINT_PY="到 https://www.python.org/downloads/ 下載安裝（勾選 Add to PATH）"; HINT_FF="winget install ffmpeg，或到 https://ffmpeg.org/download.html 下載";;
esac

line "== 自媒體 AI 員工 工具檢查（$NEED）=="
line "系統：$OS"

# Python
if command -v python3 >/dev/null 2>&1; then
  ok "python3 $(python3 --version 2>&1 | awk '{print $2}')"
  PY=python3
elif command -v python >/dev/null 2>&1; then
  ok "python $(python --version 2>&1 | awk '{print $2}')"
  PY=python
else
  miss "python3：做圖、檢查文字都要用。安裝：$HINT_PY"
  PY=""
fi

if [ "$NEED" = "carousel" ] || [ "$NEED" = "all" ]; then
  if [ -n "$PY" ]; then
    if $PY -c "import PIL" >/dev/null 2>&1; then
      ok "Pillow（Python 畫圖套件）$($PY -c 'import PIL;print(PIL.__version__)')"
    else
      miss "Pillow：把輪播文字畫成圖片要用。安裝：$PY -m pip install pillow"
    fi
    FONT_RESULT="$($PY "$(dirname "$0")/render_carousel.py" --find-font 2>/dev/null)"
    if [ -n "$FONT_RESULT" ]; then
      ok "繁體中文字型：$FONT_RESULT"
    else
      miss "繁體中文字型：圖片上的中文會變方塊。安裝 Noto Sans TC：https://fonts.google.com/noto/specimen/Noto+Sans+TC（下載後雙擊安裝）"
    fi
  fi
fi

if [ "$NEED" = "video" ] || [ "$NEED" = "all" ]; then
  if command -v ffmpeg >/dev/null 2>&1; then
    ok "ffmpeg $(ffmpeg -version 2>/dev/null | head -1 | awk '{print $3}')"
  else
    miss "ffmpeg：剪片、裁 9:16、燒字幕都要用。安裝：$HINT_FF"
  fi
  if command -v ffprobe >/dev/null 2>&1; then
    ok "ffprobe（讀影片長度與解析度）"
  else
    miss "ffprobe：通常跟 ffmpeg 一起裝，裝好 ffmpeg 就有"
  fi
  if command -v whisper >/dev/null 2>&1 || { [ -n "$PY" ] && $PY -c "import whisper" >/dev/null 2>&1; }; then
    ok "whisper（語音轉字幕）"
  elif command -v whisper-cli >/dev/null 2>&1 || command -v whisper-cpp >/dev/null 2>&1; then
    ok "whisper.cpp（語音轉字幕）"
  else
    opt "語音轉字幕工具沒裝：沒有也能剪，字幕會請你提供逐字稿或用你已有的字幕檔。想裝：pip install openai-whisper，或 brew install whisper-cpp"
  fi
fi

line ""
line "結果：有 $OK 項，缺 $MISS 項，選配 $OPT 項"
if [ "$MISS" -gt 0 ]; then
  line "缺的項目先裝好再跑一次這個檢查；沒裝之前，我會先把文案、分頁規劃與圖片規格做好交給你。"
fi
exit 0
