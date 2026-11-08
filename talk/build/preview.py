"""Rough preview of each frame in an .excalidraw file (layout check only)."""
import base64, io, json, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, sys.argv[3])
from excali import font

doc = json.load(open(sys.argv[1])); out = sys.argv[2]
els = doc["elements"]; files = doc["files"]
frames = [e for e in els if e["type"] == "frame"]
S = 0.5


def col(c):
    return None if c in (None, "transparent") else c


sheet = []
for fr in frames:
    fx, fy = fr["x"], fr["y"]
    img = Image.new("RGB", (int(fr["width"] * S), int(fr["height"] * S)), "white")
    dr = ImageDraw.Draw(img)
    P = lambda x, y: ((x - fx) * S, (y - fy) * S)
    for e in els:
        if e.get("frameId") != fr["id"]: continue
        x0, y0 = P(e["x"], e["y"]); x1, y1 = x0 + e["width"] * S, y0 + e["height"] * S
        sw = max(1, int(e["strokeWidth"] * S))
        st, bg = col(e["strokeColor"]), col(e["backgroundColor"])
        if e.get("opacity", 100) < 50: st, bg = ("#e5e5e5" if st else None), ("#f6f6f6" if bg else None)
        t = e["type"]
        if t == "rectangle":
            dr.rounded_rectangle([x0, y0, x1, y1], 8, fill=bg, outline=st, width=sw)
        elif t == "ellipse":
            dr.ellipse([x0, y0, x1, y1], fill=bg, outline=st, width=sw)
        elif t == "diamond":
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            dr.polygon([(cx, y0), (x1, cy), (cx, y1), (x0, cy)], fill=bg, outline=st, width=sw)
        elif t in ("arrow", "line"):
            pts = [P(e["x"] + px, e["y"] + py) for px, py in e["points"]]
            dr.line(pts, fill=st, width=sw + 1)
            if t == "arrow" and e.get("endArrowhead"):
                import math
                (ax, ay), (bx, by) = pts[-2], pts[-1]
                ang = math.atan2(by - ay, bx - ax)
                for da in (2.6, -2.6):
                    dr.line([(bx, by), (bx + 12 * math.cos(ang + da), by + 12 * math.sin(ang + da))], fill=st, width=sw + 1)
        elif t == "image":
            raw = files[e["fileId"]]["dataURL"].split(",", 1)[1]
            im = Image.open(io.BytesIO(base64.b64decode(raw))).convert("RGB")
            img.paste(im.resize((int(e["width"] * S), int(e["height"] * S))), (int(x0), int(y0)))
    for e in els:  # text on top
        if e.get("frameId") != fr["id"] or e["type"] != "text": continue
        x0, y0 = P(e["x"], e["y"])
        f = font(e["fontFamily"], max(6, int(e["fontSize"] * S)))
        lh = e["fontSize"] * 1.25 * S
        for i, ln in enumerate(e["text"].split("\n")):
            w = f.getlength(ln); W = e["width"] * S
            dx = (W - w) / 2 if e["textAlign"] == "center" else (W - w if e["textAlign"] == "right" else 0)
            dr.text((x0 + dx, y0 + i * lh), ln, fill=("#e0e0e0" if e.get("opacity",100) < 50 else e["strokeColor"]), font=f)
    dr.rectangle([0, 0, img.width - 1, img.height - 1], outline="#bbb")
    dr.text((8, 4), fr["name"], fill="#aaa", font=font(1, 14))
    sheet.append(img)

cols = 2
w, h = sheet[0].size
for start in range(0, len(sheet), 6):
    chunk = sheet[start:start + 6]
    rows = (len(chunk) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * w + 20, rows * h + 10 * rows), "#ddd")
    for i, im in enumerate(chunk):
        canvas.paste(im, ((i % cols) * (w + 10), (i // cols) * (h + 10)))
    canvas.save(f"{out}/preview_{start // 6 + 1}.png")
print(len(sheet), "frames previewed")
