#!/usr/bin/env python3
"""自媒體 AI 員工：把輪播規格（JSON）畫成 IG／FB 用的圖片。

用法：
  python3 render_carousel.py spec.json                 把所有頁面畫成 PNG，並做一張總覽圖
  python3 render_carousel.py spec.json --only 3        只重畫第 3 頁
  python3 render_carousel.py --find-font               只回報找到哪個繁體中文字型
  python3 render_carousel.py --example > spec.json     印出一份範例規格

規格格式（JSON）：
{
  "output_dir": "輸出資料夾（預設跟 spec.json 同層的 images/）",
  "size": [1080, 1350],
  "brand": {
    "handle": "@yourname",            # 浮水印，留空字串就不放
    "bg": "#F4F0E7", "text": "#1C2220", "accent": "#2F6B4F",
    "accent2": "#4A6B8A", "muted": "#6E6E6E",
    "font": "字型檔路徑（可省略，會自動找）", "font_bold": "粗體字型檔路徑（可省略）"
  },
  "pages": [
    {"type": "cover", "label": "小標籤", "title": "封面主標\n可換行", "subtitle": "副標", "note": "小字"},
    {"type": "text",  "heading": "頁標題", "body": "正文，可用空行分段", "note": "底部小字"},
    {"type": "list",  "heading": "頁標題", "items": ["第一點", "第二點"], "note": ""},
    {"type": "quote", "text": "一句話金句", "note": "出處或補充"},
    {"type": "cta",   "heading": "標題", "body": "說明", "action": "留言「關鍵字」"}
  ]
}
只需要 Python 3 與 Pillow（pip install pillow）。文字不夠放時會自動縮小字級，縮到底還放不下就在結尾回報。
"""
import argparse
import glob
import json
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("缺 Pillow：請先執行  python3 -m pip install pillow", file=sys.stderr)
    sys.exit(2)

HOME = os.path.expanduser("~")

# ---------- 字型 ----------
FONT_CANDIDATES = [
    # (glob 樣式, 粗體檔案候選樣式, 名稱)
    (f"{HOME}/Library/Fonts/NotoSansTC-Regular.ttf", [f"{HOME}/Library/Fonts/NotoSansTC-Bold.ttf", f"{HOME}/Library/Fonts/NotoSansTC-Medium.ttf", f"{HOME}/Library/Fonts/NotoSansTC-Black.ttf"], "Noto Sans TC"),
    (f"{HOME}/Library/Fonts/NotoSansTC-Medium.ttf", [f"{HOME}/Library/Fonts/NotoSansTC-Bold.ttf", f"{HOME}/Library/Fonts/NotoSansTC-Black.ttf"], "Noto Sans TC"),
    ("/Library/Fonts/NotoSansTC-Regular.ttf", ["/Library/Fonts/NotoSansTC-Bold.ttf", "/Library/Fonts/NotoSansTC-Medium.ttf"], "Noto Sans TC"),
    (f"{HOME}/Library/Fonts/NotoSansTC-VariableFont_wght.ttf", [], "Noto Sans TC (variable)"),
    (f"{HOME}/Library/Fonts/NotoSansCJK-Regular.ttc", [f"{HOME}/Library/Fonts/NotoSansCJK-Bold.ttc"], "Noto Sans CJK TC"),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"], "Noto Sans CJK TC"),
    ("/usr/share/fonts/truetype/noto/NotoSansTC-Regular.ttf", ["/usr/share/fonts/truetype/noto/NotoSansTC-Bold.ttf"], "Noto Sans TC"),
    ("/System/Library/Fonts/PingFang.ttc", [], "PingFang TC"),
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", [], "Hiragino Sans GB"),
    ("C:/Windows/Fonts/msjh.ttc", ["C:/Windows/Fonts/msjhbd.ttc"], "Microsoft JhengHei"),
    ("C:/Windows/Fonts/NotoSansTC-Regular.ttf", ["C:/Windows/Fonts/NotoSansTC-Bold.ttf"], "Noto Sans TC"),
]


def _face_index(path, want_words):
    """在 .ttc 裡找名稱含指定字樣的 face，找不到回 0。"""
    for i in range(0, 40):
        try:
            f = ImageFont.truetype(path, 20, index=i)
        except Exception:
            break
        name = " ".join(f.getname()).lower()
        if all(w.lower() in name for w in want_words):
            return i
    return 0


def find_font(spec_brand=None):
    """回傳 {'regular': (path, index), 'bold': (path, index), 'name': str} 或 None。"""
    b = spec_brand or {}
    if b.get("font") and os.path.exists(b["font"]):
        bold = b.get("font_bold") if b.get("font_bold") and os.path.exists(b.get("font_bold")) else b["font"]
        return {"regular": (b["font"], 0), "bold": (bold, 0), "name": os.path.basename(b["font"])}
    for pat, bold_pats, name in FONT_CANDIDATES:
        for path in glob.glob(pat):
            try:
                ImageFont.truetype(path, 20)
            except Exception:
                continue
            reg_idx = 0
            bold = (path, 0)
            if path.lower().endswith(".ttc"):
                if "cjk" in path.lower():
                    reg_idx = _face_index(path, ["tc"])
                    bold = (path, reg_idx)
                elif "pingfang" in path.lower():
                    reg_idx = _face_index(path, ["tc", "regular"])
                    bold = (path, _face_index(path, ["tc", "semibold"]))
                elif "hiragino" in path.lower():
                    reg_idx = _face_index(path, ["w3"])
                    bold = (path, _face_index(path, ["w6"]))
            for bp in bold_pats:
                if os.path.exists(bp):
                    bold = (bp, 0)
                    break
            return {"regular": (path, reg_idx), "bold": bold, "name": name}
    return None


class Fonts:
    def __init__(self, info):
        self.info = info
        self.cache = {}

    def get(self, size, bold=False):
        key = (size, bold)
        if key in self.cache:
            return self.cache[key]
        if self.info is None:
            f = ImageFont.load_default()
        else:
            path, idx = self.info["bold" if bold else "regular"]
            f = ImageFont.truetype(path, size, index=idx)
            if bold and "variable" in self.info["name"].lower():
                try:
                    f.set_variation_by_name("Bold")
                except Exception:
                    pass
        self.cache[key] = f
        return f

    def fake_bold(self):
        """粗體與一般字是同一個 face 時，用描邊補一點粗度。"""
        return self.info is None or self.info["bold"] == self.info["regular"]


# ---------- 文字排版 ----------
def _tokens(text):
    """把文字切成可換行的單位：中文逐字，英文數字整個詞，空白單獨。"""
    out, buf = [], ""
    for ch in text:
        if ch.isascii() and not ch.isspace():
            buf += ch
        else:
            if buf:
                out.append(buf)
                buf = ""
            out.append(ch)
    if buf:
        out.append(buf)
    return out


NO_LINE_START = "，。、：；！？」』）】〕》”’…"


def wrap(text, font, max_width, draw):
    lines = []
    for para in text.split("\n"):
        if para.strip() == "":
            lines.append("")
            continue
        cur = ""
        for tok in _tokens(para):
            trial = cur + tok
            if draw.textlength(trial, font=font) <= max_width or cur == "":
                cur = trial
            else:
                if tok in NO_LINE_START and cur:
                    cur = cur + tok
                    continue
                lines.append(cur.rstrip())
                cur = tok.lstrip()
        lines.append(cur.rstrip())
    return lines


def fit_text(draw, text, fonts, size, bold, max_width, max_height, min_size, line_gap):
    """從指定字級往下縮，直到整段放得下。回 (font, lines, size, fits)。"""
    s = size
    while True:
        f = fonts.get(s, bold)
        lines = wrap(text, f, max_width, draw)
        h = len(lines) * s * line_gap
        if h <= max_height or s <= min_size:
            return f, lines, s, h <= max_height
        s -= 2


def draw_lines(draw, x, y, lines, font, size, color, line_gap, align="left", width=None, stroke=0):
    for ln in lines:
        if align == "center" and width:
            w = draw.textlength(ln, font=font)
            xx = x + (width - w) / 2
        else:
            xx = x
        draw.text((xx, y), ln, font=font, fill=color, stroke_width=stroke, stroke_fill=color if stroke else None)
        y += size * line_gap
    return y


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------- 各頁型 ----------
def render_page(page, idx, total, spec, fonts, warn):
    W, H = spec.get("size", [1080, 1350])
    b = spec["brand"]
    bg, text, accent, accent2, muted = (hex_to_rgb(b.get(k, d)) for k, d in [
        ("bg", "#F4F0E7"), ("text", "#1C2220"), ("accent", "#2F6B4F"), ("accent2", "#4A6B8A"), ("muted", "#6E6E6E")])
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    M = int(W * 0.085)          # 邊界
    CW = W - 2 * M              # 內容寬
    stroke = 1 if fonts.fake_bold() else 0
    ptype = page.get("type", "text")
    footer_top = H - M - 10
    scale = W / 1080

    # 頂部標籤（藥丸）
    y = M
    label = page.get("label")
    if label:
        f = fonts.get(int(30 * scale), True)
        tw = d.textlength(label, font=f)
        ph = int(56 * scale)
        d.rounded_rectangle([M, y, M + tw + 48 * scale, y + ph], radius=ph // 2, fill=accent)
        d.text((M + 24 * scale, y + ph / 2 - int(30 * scale) * 0.62), label, font=f, fill=bg)
        y += ph + int(40 * scale)

    # 頁尾：浮水印與頁碼
    handle = b.get("handle", "")
    ff = fonts.get(int(30 * scale))
    if handle:
        d.text((M, footer_top - int(30 * scale)), handle, font=ff, fill=muted)
    if ptype != "cover" and total > 1:
        pn = f"{idx:02d} / {total:02d}"
        d.text((W - M - d.textlength(pn, font=ff), footer_top - int(30 * scale)), pn, font=ff, fill=muted)
    content_bottom = footer_top - int(80 * scale)

    if ptype == "cover":
        title = page.get("title", "")
        subtitle = page.get("subtitle", "")
        note = page.get("note", "")
        f_t, lines_t, s_t, ok = fit_text(d, title, fonts, int(104 * scale), True, CW, int(H * 0.42), int(60 * scale), 1.22)
        if not ok:
            warn.append(f"第 {idx} 頁封面主標太長，已縮到最小字級仍超出，請縮短主標。")
        block_h = len(lines_t) * s_t * 1.22
        sub_lines, f_s, s_s = [], None, 0
        if subtitle:
            f_s, sub_lines, s_s, _ = fit_text(d, subtitle, fonts, int(46 * scale), False, CW, int(H * 0.2), int(30 * scale), 1.5)
            block_h += 40 * scale + len(sub_lines) * s_s * 1.5
        top = max(y + 20 * scale, (H - block_h) / 2 - 60 * scale)
        yy = draw_lines(d, M, top, lines_t, f_t, s_t, text, 1.22, stroke=stroke)
        # 筆刷感重點線
        bar_y = yy + int(s_t * 0.22)
        d.rounded_rectangle([M, bar_y, M + int(160 * scale), bar_y + int(14 * scale)], radius=7, fill=accent)
        yy = bar_y + int(40 * scale)
        if subtitle:
            yy = draw_lines(d, M, yy, sub_lines, f_s, s_s, muted, 1.5)
        if note:
            fn = fonts.get(int(30 * scale))
            d.text((M, content_bottom - int(30 * scale)), note, font=fn, fill=accent2)

    elif ptype in ("text", "list"):
        heading = page.get("heading", "")
        note = page.get("note", "")
        if heading:
            f_h, lines_h, s_h, ok = fit_text(d, heading, fonts, int(66 * scale), True, CW, int(H * 0.22), int(44 * scale), 1.25)
            if not ok:
                warn.append(f"第 {idx} 頁標題太長，請縮短。")
            y = draw_lines(d, M, y, lines_h, f_h, s_h, accent, 1.25, stroke=stroke)
            y += int(34 * scale)
        avail_h = content_bottom - y - (int(70 * scale) if note else 0)
        if ptype == "text":
            body = page.get("body", "")
            f_b, lines_b, s_b, ok = fit_text(d, body, fonts, int(44 * scale), False, CW, avail_h, int(30 * scale), 1.6)
            if not ok:
                warn.append(f"第 {idx} 頁正文太多，已縮到最小字級仍超出，請拆頁或刪減。")
            used = len(lines_b) * s_b * 1.6
            y += int(max(0, min((avail_h - used) * 0.32, 260 * scale)))
            y = draw_lines(d, M, y, lines_b, f_b, s_b, text, 1.6)
        else:
            items = page.get("items", [])
            size = int(42 * scale)
            # 先試字級，整組放得下為止
            while True:
                f_i = fonts.get(size)
                total_h, prepared = 0, []
                for it in items:
                    ls = wrap(it, f_i, CW - int(78 * scale), d)
                    prepared.append(ls)
                    total_h += len(ls) * size * 1.55 + int(28 * scale)
                if total_h <= avail_h or size <= int(28 * scale):
                    break
                size -= 2
            if total_h > avail_h:
                warn.append(f"第 {idx} 頁清單太多，請拆頁或刪減。")
            y += int(max(0, min((avail_h - total_h) * 0.32, 260 * scale)))
            for n, ls in enumerate(prepared, 1):
                r = int(24 * scale)
                cy = y + size * 0.8
                d.ellipse([M, cy - r, M + 2 * r, cy + r], fill=accent)
                fnum = fonts.get(int(26 * scale), True)
                num = str(n)
                d.text((M + r - d.textlength(num, font=fnum) / 2, cy - int(26 * scale) * 0.62), num, font=fnum, fill=bg)
                y = draw_lines(d, M + int(78 * scale), y, ls, f_i, size, text, 1.55)
                y += int(28 * scale)
        if note:
            fn = fonts.get(int(30 * scale))
            nl = wrap(note, fn, CW, d)[:2]
            draw_lines(d, M, content_bottom - len(nl) * int(30 * scale) * 1.4, nl, fn, int(30 * scale), muted, 1.4)

    elif ptype == "quote":
        qt = page.get("text", "")
        note = page.get("note", "")
        fq = fonts.get(int(160 * scale), True)
        d.text((M - int(10 * scale), int(H * 0.22)), "“", font=fq, fill=accent2)
        f_q, lines_q, s_q, ok = fit_text(d, qt, fonts, int(72 * scale), True, CW, int(H * 0.45), int(44 * scale), 1.4)
        if not ok:
            warn.append(f"第 {idx} 頁金句太長，請縮短。")
        block_h = len(lines_q) * s_q * 1.4
        top = (H - block_h) / 2
        draw_lines(d, M, top, lines_q, f_q, s_q, text, 1.4, stroke=stroke)
        if note:
            fn = fonts.get(int(32 * scale))
            d.text((M, top + block_h + int(40 * scale)), note, font=fn, fill=muted)

    elif ptype == "cta":
        heading = page.get("heading", "")
        body = page.get("body", "")
        action = page.get("action", "")
        yy = max(y, int(H * 0.26))
        if heading:
            f_h, lines_h, s_h, ok = fit_text(d, heading, fonts, int(76 * scale), True, CW, int(H * 0.25), int(46 * scale), 1.25)
            yy = draw_lines(d, M, yy, lines_h, f_h, s_h, text, 1.25, stroke=stroke) + int(30 * scale)
        if body:
            f_b, lines_b, s_b, ok = fit_text(d, body, fonts, int(42 * scale), False, CW, int(H * 0.25), int(30 * scale), 1.6)
            if not ok:
                warn.append(f"第 {idx} 頁說明太長，請縮短。")
            yy = draw_lines(d, M, yy, lines_b, f_b, s_b, muted, 1.6) + int(50 * scale)
        if action:
            fa = fonts.get(int(46 * scale), True)
            al = wrap(action, fa, CW - int(80 * scale), d)
            bh = int(len(al) * 46 * scale * 1.4 + 56 * scale)
            box_top = min(yy, content_bottom - bh)
            d.rounded_rectangle([M, box_top, W - M, box_top + bh], radius=int(28 * scale), fill=accent)
            draw_lines(d, M, box_top + int(28 * scale), al, fa, int(46 * scale), bg, 1.4, align="center", width=CW)
    else:
        warn.append(f"第 {idx} 頁 type「{ptype}」不認識，已畫成空白頁。")
    return img


def contact_sheet(paths, out_path, cols=4):
    thumbs = [Image.open(p) for p in paths]
    if not thumbs:
        return
    tw = 360
    th = int(thumbs[0].height * tw / thumbs[0].width)
    rows = (len(thumbs) + cols - 1) // cols
    gap = 16
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * gap, rows * th + (rows + 1) * gap), (230, 230, 230))
    for i, im in enumerate(thumbs):
        im = im.resize((tw, th))
        x = gap + (i % cols) * (tw + gap)
        y = gap + (i // cols) * (th + gap)
        sheet.paste(im, (x, y))
    sheet.save(out_path)


EXAMPLE = {
    "output_dir": "images",
    "size": [1080, 1350],
    "brand": {"handle": "@yourname", "bg": "#F4F0E7", "text": "#1C2220", "accent": "#2F6B4F", "accent2": "#4A6B8A", "muted": "#6E6E6E"},
    "pages": [
        {"type": "cover", "label": "AI 工作術", "title": "會議結束\n待辦三分鐘整理完", "subtitle": "把錄音丟給 AI，照這個順序做", "note": "實測於 2026 年 11 月"},
        {"type": "text", "heading": "以前的做法", "body": "開完會回座位，先回訊息，再翻筆記，常常漏掉誰答應了什麼。\n\n等到隔天才發現，有一件事根本沒人接。"},
        {"type": "list", "heading": "現在這樣做", "items": ["會議錄音或筆記整段貼給 AI", "請它列出「誰、做什麼、什麼時候」", "自己核對一次，不確定的標出來"], "note": "整段流程大約三分鐘"},
        {"type": "quote", "text": "AI 負責整理，人負責確認。", "note": "順序不要反過來"},
        {"type": "cta", "heading": "想要我用的指令範本", "body": "我把整段提示詞和檢查清單整理成一頁。", "action": "留言「待辦」我私訊你"}
    ]
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--only", type=int, help="只重畫第 N 頁（從 1 數）")
    ap.add_argument("--find-font", action="store_true")
    ap.add_argument("--example", action="store_true")
    args = ap.parse_args()

    if args.example:
        print(json.dumps(EXAMPLE, ensure_ascii=False, indent=2))
        return
    if args.find_font:
        info = find_font()
        if info:
            print(f"{info['name']}（{info['regular'][0]}）")
            sys.exit(0)
        sys.exit(1)
    if not args.spec:
        ap.print_help()
        sys.exit(1)

    with open(args.spec, encoding="utf-8") as fh:
        spec = json.load(fh)
    spec.setdefault("brand", {})
    info = find_font(spec["brand"])
    if info is None:
        print("找不到繁體中文字型。請安裝 Noto Sans TC（https://fonts.google.com/noto/specimen/Noto+Sans+TC），或在 brand.font 指定字型檔路徑。", file=sys.stderr)
        sys.exit(3)
    fonts = Fonts(info)
    base = os.path.dirname(os.path.abspath(args.spec))
    out_dir = spec.get("output_dir") or "images"
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(base, out_dir)
    os.makedirs(out_dir, exist_ok=True)

    pages = spec.get("pages", [])
    total = len(pages)
    warn = []
    written = []
    for i, page in enumerate(pages, 1):
        name = f"{i:02d}_{page.get('type', 'page')}.png"
        path = os.path.join(out_dir, name)
        if args.only and i != args.only:
            written.append(path)
            continue
        img = render_page(page, i, total, spec, fonts, warn)
        img.save(path, "PNG")
        written.append(path)
        print(f"已畫：{path}")
    existing = [p for p in written if os.path.exists(p)]
    sheet = os.path.join(out_dir, "00_overview.png")
    contact_sheet(existing, sheet)
    print(f"總覽：{sheet}")
    print(f"字型：{info['name']}")
    if warn:
        print("需要注意：")
        for w in warn:
            print(f"  - {w}")
    else:
        print("所有頁面文字都放得下。")


if __name__ == "__main__":
    main()
