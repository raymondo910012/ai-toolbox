---
name: create_ppt
description: 使用 python-pptx 建立或修改 PPT 簡報。套用 EC (Edgecore) 模板背景，內容排版參考 Kiro_Introduction 風格。適用於需要產生投影片的場景。
---

# create_ppt

使用 python-pptx 產生 PPT，套用 EC 模板背景 + Kiro_Introduction 排版風格。

## 模板與風格規範

### 模板來源
- EC 模板路徑：`D:\Kiro\project\ppt\Edgecore ppt format 2026_v0116_1_02.pptx`
- 封面 layout：`1_Cover-1`（layout index 0）
- 內容頁 layout：`2_只有標題`（layout index 25），含 placeholder idx=0 (title), idx=2 (body), idx=10 (right)

### 排版風格（參考 Kiro_Introduction_20260416）
- 字體：`Microsoft JhengHei`（微軟正黑體）
- 標題：30pt, bold, color `#0F172A`
- 內文：18pt, color `#0F172A`, word_wrap=True, space_after=Pt(10)
- 副標/灰字：24pt, color `#64748B`
- Accent 色：`#430A6D`（紫）、`#3A99A6`（teal）

### 背景卡片
- 使用 `MSO_SHAPE.ROUNDED_RECTANGLE` 作為內容區淡色背景
- 填色：`#F5F0FA`（極淡紫）
- 邊框：`#E2E8F0`, 1pt
- 位置：`left=800000, top=1750000, width=10550000, height=4400000`（EMU）
- 必須 send to back（insert at index 2 in spTree）

### 頁面結構
1. **封面**：用 cover layout，文字放投影片下方（top≈5000000）避免被背景圖擋住
2. **內容頁**：
   - Title placeholder (idx=0)：放題目標題，30pt bold
   - 移除 placeholder idx=2（副標）和 idx=10（右側空白）
   - 用 `add_textbox` 加入內文，位置 `left=914400, top=1828800, width=10332720`
   - 加入淡色圓角矩形背景卡片
3. **結尾頁**：用 cover layout，放 "Thank You"

## Script 範本

```python
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.shapes.placeholder import _InheritsDimensions

# === 常數 ===
TEMPLATE = r'D:\Kiro\project\ppt\Edgecore ppt format 2026_v0116_1_02.pptx'
FONT = 'Microsoft JhengHei'
CLR_TITLE = RGBColor(0x0F, 0x17, 0x2A)
CLR_BODY = RGBColor(0x0F, 0x17, 0x2A)
CLR_GREY = RGBColor(0x64, 0x74, 0x8B)
CLR_CARD_BG = RGBColor(0xF5, 0xF0, 0xFA)
CLR_CARD_BORDER = RGBColor(0xE2, 0xE8, 0xF0)

# === 載入模板 ===
prs = Presentation(TEMPLATE)

# 清除模板既有 slides
while len(prs.slides) > 0:
    rId = prs.slides._sldIdLst[0].rId
    prs.part.drop_rel(rId)
    prs.slides._sldIdLst.remove(prs.slides._sldIdLst[0])

cover_layout = prs.slide_layouts[0]
content_layout = prs.slide_layouts[25]

# === Helper ===
def add_cover(prs, title, subtitle=''):
    s = prs.slides.add_slide(cover_layout)
    box = s.shapes.add_textbox(Emu(914400), Emu(5000000), Emu(10332720), Emu(1000000))
    p = box.text_frame.paragraphs[0]
    p.text = title
    p.font.name = FONT
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = CLR_TITLE
    p.alignment = PP_ALIGN.CENTER
    if subtitle:
        box2 = s.shapes.add_textbox(Emu(914400), Emu(5700000), Emu(10332720), Emu(600000))
        p2 = box2.text_frame.paragraphs[0]
        p2.text = subtitle
        p2.font.name = FONT
        p2.font.size = Pt(24)
        p2.font.color.rgb = CLR_GREY
        p2.alignment = PP_ALIGN.CENTER
    return s

def add_content_slide(prs, title, body_lines):
    s = prs.slides.add_slide(content_layout)
    # 設定標題
    to_remove = []
    for shape in s.shapes:
        if isinstance(shape, _InheritsDimensions):
            idx = shape.placeholder_format.idx
            if idx == 0:
                tf = shape.text_frame
                tf.paragraphs[0].text = title
                tf.paragraphs[0].font.name = FONT
                tf.paragraphs[0].font.size = Pt(30)
                tf.paragraphs[0].font.bold = True
                tf.paragraphs[0].font.color.rgb = CLR_TITLE
            elif idx in (2, 10):
                to_remove.append(shape)
    for shape in to_remove:
        shape._element.getparent().remove(shape._element)

    # 背景卡片
    card = s.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Emu(800000), Emu(1750000), Emu(10550000), Emu(4400000)
    )
    card.fill.solid()
    card.fill.fore_color.rgb = CLR_CARD_BG
    card.line.color.rgb = CLR_CARD_BORDER
    card.line.width = Pt(1)
    sp = card._element
    spTree = sp.getparent()
    spTree.remove(sp)
    spTree.insert(2, sp)

    # 內文
    box = s.shapes.add_textbox(Emu(914400), Emu(1828800), Emu(10332720), Emu(4500000))
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(body_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.name = FONT
        p.font.size = Pt(18)
        p.font.color.rgb = CLR_BODY
        p.space_after = Pt(10)
    return s

# === 使用範例 ===
add_cover(prs, '簡報標題', '副標題')

add_content_slide(prs, 'Q1：題目標題', [
    '第一行內容',
    '第二行內容',
    '',
    '• bullet point'
])

add_cover(prs, 'Thank You')

prs.save('output.pptx')
```

## 注意事項
- EC 模板的 cover layout 背景圖群組左邊可能超出投影片，如需修正可設 `shape.left = 0`
- 內容頁不要使用副標 placeholder（idx=2）和右側空白（idx=10），直接移除
- 背景卡片顏色用極淡紫 `#F5F0FA`，不要太深
- 文字框要設 `word_wrap = True` 確保長文自動換行
- 存檔前確認 PowerPoint 沒有開啟該檔案（會 PermissionError）
