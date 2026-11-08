import sys
from PIL import Image, ImageDraw, ImageFont
src, out = sys.argv[1], sys.argv[2]
lines = ["$ python3 lint_lineage.py --target FEMA_NRI.risk_score \\",
         "      --covariates ACS.EP_POV150 ACS.EP_UNEMP", ""]
for l in open(src).read().splitlines():
    if l.startswith("──") or l.strip() == "custom": continue
    if "R2 against it" in l or "NOTE" in l: continue
    lines.append(l)
lines += ["", "$ echo $?", "1"]
F = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 24)
B = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 24, index=1)
cw = F.getlength("M"); lh = 36
W = int(max(len(l) for l in lines) * cw + 80); H = len(lines) * lh + 110
img = Image.new("RGB", (W, H), "#1e1e1e"); d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 50], fill="#343a40")
for i, c in enumerate(["#ff6b6b", "#ffd43b", "#69db7c"]):
    d.ellipse([22 + i * 32, 16, 40 + i * 32, 34], fill=c)
y = 72
for l in lines:
    col, font = "#e9ecef", F
    if l.startswith("$"): col = "#69db7c"
    elif "FAIL" in l or "ERROR" in l: col, font = "#ff6b6b", B
    elif "->" in l: col = "#74c0fc"
    elif l.strip().startswith("["): col = "#adb5bd"
    elif l.strip() == "1": col, font = "#ff6b6b", B
    d.text((40, y), l, fill=col, font=font); y += lh
img.save(out)
print(W, H)
