"""Tiny Excalidraw scene builder: frames, boxes, arrows, text, images."""
import base64, hashlib, json, math, random, time
from PIL import Image, ImageFont

FONT_DIR = "/private/tmp/claude-501/-Users-kayodeadeniyi-dev-dependency-manifest/fba2f02e-3bc7-4290-a266-57f1910a93df/scratchpad/fonts"
_fonts = {}


def font(family, size):
    key = (family, size)
    if key not in _fonts:
        if family == 3:
            _fonts[key] = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", size)
        else:
            _fonts[key] = ImageFont.truetype(f"{FONT_DIR}/Virgil.otf", size)
    return _fonts[key]


def measure(s, size, family=1):
    f = font(family, size)
    lines = s.split("\n")
    return max(f.getlength(l) for l in lines), len(lines) * size * 1.25


INK, GREY = "#1e1e1e", "#868e96"
COL = {  # stroke, fill
    "ink": ("#1e1e1e", "transparent"),
    "red": ("#e03131", "#ffc9c9"),
    "green": ("#2f9e44", "#b2f2bb"),
    "blue": ("#1971c2", "#a5d8ff"),
    "yellow": ("#f08c00", "#ffec99"),
    "grey": ("#868e96", "#e9ecef"),
    "violet": ("#6741d9", "#d0bfff"),
    "orange": ("#e8590c", "#ffd8a8"),
    "white": ("#1e1e1e", "#ffffff"),
    "dark": ("#1e1e1e", "#1e1e1e"),
}
W, H, GAP = 1920, 1080, 260
rng = random.Random(7)


def uid():
    return "".join(rng.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(16))


class Deck:
    def __init__(self):
        self.els, self.files, self.frame, self.n = [], {}, None, 0
        self.ox = self.oy = 0
        self.notes = []

    def _base(self, typ, x, y, w, h, stroke=INK, bg="transparent", **kw):
        e = dict(id=uid(), type=typ, x=x, y=y, width=w, height=h, angle=0,
                 strokeColor=stroke, backgroundColor=bg, fillStyle="solid",
                 strokeWidth=2, strokeStyle="solid", roughness=1, opacity=100,
                 groupIds=[], frameId=self.frame, roundness=None,
                 seed=rng.randint(1, 2**31), version=1,
                 versionNonce=rng.randint(1, 2**31), isDeleted=False,
                 boundElements=[], updated=int(time.time() * 1000), link=None,
                 locked=False)
        e.update(kw)
        self.els.append(e)
        return e

    # ------------------------------------------------------------ slides
    def slide(self, title, notes=""):
        self.n += 1
        self.ox, self.oy = 0, (self.n - 1) * (H + GAP)
        name = f"{self.n:02d} {title}"
        fr = self._base("frame", self.ox, self.oy, W, H, stroke="#bbb", name=name)
        self.frame = fr["id"]
        self.notes.append((name, notes))
        if notes:  # speaker notes sit outside the frame, so they never show
            saved, self.frame = self.frame, None
            self.text(W + 80, 0, "Notes\n\n" + notes, 26, GREY, family=1, absolute=False)
            self.frame = saved

    def title(self, s, size=72, color=INK):
        return self.text(110, 80, s, size, color)

    # ------------------------------------------------------------ text
    def text(self, x, y, s, size=40, color=INK, align="left", family=1,
             absolute=False, container=None, opacity=100):
        tw, th = measure(s, size, family)
        if align == "center" and container is None:
            x = x - tw / 2
        elif align == "right" and container is None:
            x = x - tw
        ax, ay = (x, y) if absolute or container else (self.ox + x, self.oy + y)
        e = self._base("text", ax, ay, tw, th, stroke=color, text=s, fontSize=size,
                       fontFamily=family, textAlign=align,
                       verticalAlign="middle" if container else "top",
                       containerId=container, originalText=s, autoResize=True,
                       lineHeight=1.25, opacity=opacity)
        return e

    # ------------------------------------------------------------ shapes
    def box(self, x, y, w, h, label=None, col="ink", size=36, shape="rectangle",
            dashed=False, color=None, family=1, sw=2, label_color=None):
        stroke, bg = COL[col]
        if color: stroke = color
        e = self._base(shape, self.ox + x, self.oy + y, w, h, stroke=stroke, bg=bg,
                       strokeStyle="dashed" if dashed else "solid", strokeWidth=sw,
                       roundness={"type": 3} if shape == "rectangle" else {"type": 2})
        if label:
            tw, th = measure(label, size, family)
            t = self.text(e["x"] + (w - tw) / 2, e["y"] + (h - th) / 2, label, size,
                          label_color or ("#ffffff" if col == "dark" else INK),
                          align="center", family=family, container=e["id"])
            e["boundElements"].append({"type": "text", "id": t["id"]})
        return e

    def pill(self, x, y, label, col="red", size=30, pad=22):
        tw, th = measure(label, size)
        return self.box(x, y, tw + pad * 2, th + 16, label, col, size)

    @staticmethod
    def _edge(b, tx, ty, gap=6):
        cx, cy = b["x"] + b["width"] / 2, b["y"] + b["height"] / 2
        dx, dy = tx - cx, ty - cy
        if dx == 0 and dy == 0:
            return cx, cy
        hw, hh = b["width"] / 2 + gap, b["height"] / 2 + gap
        if b["type"] == "ellipse":
            t = 1 / math.sqrt((dx / hw) ** 2 + (dy / hh) ** 2)
        elif b["type"] == "diamond":
            t = 1 / (abs(dx) / hw + abs(dy) / hh)
        else:
            t = min(hw / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
        return cx + dx * t, cy + dy * t

    def arrow(self, a, b, col="ink", label=None, dashed=False, size=26, sw=2,
              head="arrow", start_head=None, color=None):
        stroke = color or COL[col][0]
        acx, acy = a["x"] + a["width"] / 2, a["y"] + a["height"] / 2
        bcx, bcy = b["x"] + b["width"] / 2, b["y"] + b["height"] / 2
        x1, y1 = self._edge(a, bcx, bcy)
        x2, y2 = self._edge(b, acx, acy)
        e = self._base("arrow", x1, y1, abs(x2 - x1), abs(y2 - y1), stroke=stroke,
                       strokeStyle="dashed" if dashed else "solid", strokeWidth=sw,
                       roundness={"type": 2}, points=[[0, 0], [x2 - x1, y2 - y1]],
                       lastCommittedPoint=None,
                       startBinding={"elementId": a["id"], "focus": 0, "gap": 6},
                       endBinding={"elementId": b["id"], "focus": 0, "gap": 6},
                       startArrowhead=start_head, endArrowhead=head, elbowed=False)
        a["boundElements"].append({"type": "arrow", "id": e["id"]})
        b["boundElements"].append({"type": "arrow", "id": e["id"]})
        if label:
            tw, th = measure(label, size)
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            t = self.text(mx - tw / 2, my - th / 2, label, size, stroke,
                          align="center", container=e["id"])
            e["boundElements"].append({"type": "text", "id": t["id"]})
        return e

    def line(self, pts, col="ink", sw=3, dashed=False, color=None, arrowhead=None):
        stroke = color or COL[col][0]
        x0, y0 = pts[0]
        rel = [[px - x0, py - y0] for px, py in pts]
        xs, ys = [p[0] for p in rel], [p[1] for p in rel]
        typ = "arrow" if arrowhead else "line"
        return self._base(typ, self.ox + x0, self.oy + y0, max(xs) - min(xs),
                          max(ys) - min(ys), stroke=stroke, strokeWidth=sw,
                          strokeStyle="dashed" if dashed else "solid",
                          roundness={"type": 2}, points=rel, lastCommittedPoint=None,
                          startBinding=None, endBinding=None, startArrowhead=None,
                          endArrowhead=arrowhead, **({"elbowed": False} if arrowhead else {}))

    def tick(self, x, y, s=44, col="green"):
        return self.line([(x, y + s * .5), (x + s * .38, y + s * .9), (x + s, y)], col, sw=5)

    def cross(self, x, y, s=40, col="red"):
        self.line([(x, y), (x + s, y + s)], col, sw=5)
        self.line([(x + s, y), (x, y + s)], col, sw=5)

    def strike(self, el, col="red"):
        x, y = el["x"] - self.ox, el["y"] - self.oy
        self.line([(x - 10, y + el["height"] / 2), (x + el["width"] + 10, y + el["height"] / 2)], col, sw=5)

    # ------------------------------------------------------------ icons
    def doc(self, x, y, w=150, h=190, label=None, col="white", size=30, lines=3):
        """A page with a folded corner and a few text lines."""
        b = self.box(x, y, w, h, None, col)
        f = w * .25
        self.line([(x + w - f, y), (x + w - f, y + f), (x + w, y + f)], "ink", sw=2)
        for i in range(lines):
            ly = y + h * .38 + i * h * .16
            self.line([(x + w * .18, ly), (x + w * (.82 if i < lines - 1 else .55), ly)], "grey", sw=3)
        if label:
            self.text(x + w / 2, y + h + 12, label, size, align="center")
        return b

    def pdf_stack(self, x, y, w=150, h=190, label="PDF", n=3):
        for i in range(n - 1, -1, -1):
            b = self.doc(x + i * 22, y + i * 18, w, h, None, "white", lines=3)
        self.pill(x + w * .12, y + h * .08, label, "red", 26, pad=12)
        return b

    def scale(self, x, y, w=220):
        """Bathroom scale: platform, dial, needle."""
        b = self.box(x, y, w, w * .9, None, "grey")
        d = self.box(x + w * .3, y + w * .14, w * .4, w * .28, None, "white", shape="ellipse")
        self.line([(x + w * .5, y + w * .34), (x + w * .6, y + w * .2)], "red", sw=3)
        return b

    def ruler(self, x, y, w=90, h=300):
        b = self.box(x, y, w, h, None, "yellow")
        for i in range(1, 10):
            ty = y + i * h / 10
            self.line([(x, ty), (x + (w * .45 if i % 5 == 0 else w * .25), ty)], "ink", sw=2)
        return b

    def warn(self, x, y, s=120, col="yellow"):
        stroke, bg = {"yellow": ("#f08c00", "#ffec99"), "red": ("#e03131", "#ffc9c9")}[col]
        e = self.line([(x + s / 2, y), (x + s, y + s * .88), (x, y + s * .88), (x + s / 2, y)],
                      color=stroke, sw=4)
        e["backgroundColor"] = bg; e["roundness"] = None
        self.text(x + s / 2, y + s * .25, "!", int(s * .5), stroke, align="center")
        return e

    def curve(self, pts, col="ink", sw=3, dashed=False, color=None, head="arrow"):
        return self.line(pts, col, sw, dashed, color, arrowhead=head)

    def badge(self, x, y, s, col="green", mark="tick"):
        self.box(x, y, s, s, None, col, shape="ellipse")
        if mark == "tick":
            self.tick(x + s * .22, y + s * .3, s * .56, col)
        else:
            self.cross(x + s * .28, y + s * .28, s * .44, col)

    def person(self, x, y, s=80, col="ink"):
        self.box(x + s * .3, y, s * .4, s * .4, None, col, shape="ellipse")
        self.line([(x + s * .1, y + s), (x + s * .2, y + s * .55), (x + s * .8, y + s * .55),
                   (x + s * .9, y + s)], col, sw=3)

    # ------------------------------------------------------------ images
    def image(self, path, x, y, w=None, h=None):
        raw = open(path, "rb").read()
        fid = hashlib.sha1(raw).hexdigest()
        iw, ih = Image.open(path).size
        if w and not h: h = w * ih / iw
        if h and not w: w = h * iw / ih
        now = int(time.time() * 1000)
        self.files[fid] = {"mimeType": "image/png", "id": fid, "created": now,
                           "lastRetrieved": now,
                           "dataURL": "data:image/png;base64," + base64.b64encode(raw).decode()}
        return self._base("image", self.ox + x, self.oy + y, w, h, fileId=fid,
                          status="saved", scale=[1, 1], crop=None,
                          strokeColor="transparent")

    def save(self, path):
        doc = {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
               "elements": self.els,
               "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None,
                            "currentItemFontFamily": 1},
               "files": self.files}
        json.dump(doc, open(path, "w"))
