import sys
sys.path.insert(0, sys.argv[1])
from excali import Deck, measure, COL

IMG, OUT = sys.argv[2], sys.argv[3]
d = Deck()
from notes import NOTES
_slide = d.slide
d.slide = lambda title, notes='': _slide(title, NOTES[title])
GREY, RED, GREEN, BLUE, VIO, ORANGE = "#868e96", "#e03131", "#2f9e44", "#1971c2", "#6741d9", "#e8590c"


def chain_base():
    """The FEMA graph, used by the three build slides."""
    n = {}
    n["pov"] = d.box(330, 190, 300, 90, "ACS poverty", "blue", 32)
    n["une"] = d.box(820, 190, 380, 90, "ACS unemployment", "red", 32, sw=3)
    n["cre"] = d.box(330, 410, 420, 100, "Census estimate", "violet", 32)
    n["bric"] = d.box(1160, 410, 380, 100, "BRIC index", "orange", 32)
    n["sv"] = d.box(330, 630, 420, 90, "social vulnerability", "white", 30)
    n["cr"] = d.box(1160, 630, 380, 90, "community resilience", "white", 30)
    n["risk"] = d.box(760, 860, 400, 110, "FEMA risk score", "yellow", 40, sw=3)
    return n


def fade(n, keys):
    ids = {n[k]["id"] for k in keys}
    for e in d.els:
        if e["id"] in ids or e.get("containerId") in ids:
            e["opacity"] = 12


# ============================================================ ACT 1: the story
# ---------------------------------------------------------------- 1 title
d.slide("Title", "Hello, Kayode here.\nTonight: a bug no test caught,\nand how a graph shows it to you.\nYou won't need any Python to follow.")
d.text(960, 110, "The Dependency Graph\nYour Tests Can't See", 100, align="center")
a = d.box(360, 660, 300, 120, "input", "blue", 44)
q = d.box(810, 450, 300, 110, "?", "grey", 56, dashed=True)
t = d.box(1260, 660, 300, 120, "target", "yellow", 44)
d.arrow(a, t, label="model", size=32, sw=3)
d.arrow(a, q, "grey", dashed=True); d.arrow(q, t, "grey", dashed=True)
d.text(960, 880, "Kayode Adeniyi", 44, align="center")
d.text(960, 950, "JS Monthly London  ·  12 November 2026", 32, GREY, align="center")

# ---------------------------------------------------------------- 2 circular import
d.slide("Seen this?", "Hands up if you've seen this warning.\na.js imports b.js, and b.js imports a.js.\nOur bundler spots the loop and tells us.\nWe never have to go looking for it.")
d.title("Seen this?", 80)
d.doc(420, 260, 200, 250, "a.js", "white", 44)
d.doc(1300, 260, 200, 250, "b.js", "white", 44)
d.curve([(650, 300), (960, 200), (1270, 300)], "red", sw=5)
d.curve([(1270, 480), (960, 580), (650, 480)], "red", sw=5)
d.text(960, 150, "imports", 32, RED, align="center")
d.text(960, 600, "imports", 32, RED, align="center")
d.box(360, 720, 1200, 230, None, "dark")
d.warn(410, 770, 110)
d.text(570, 775, "Circular dependency detected:\nsrc/a.js -> src/b.js -> src/a.js", 40, "#ffd43b", family=3)

# ---------------------------------------------------------------- 3 BMI
d.slide("BMI", "Something we all see at the doctor or on a fitness app.\nBMI is made from two numbers: weight and height.\nSay a model predicts BMI from weight and height.\nIt scores 0.998.\nNobody in this room would be impressed.\nWe all know the formula.")
d.title("Predict BMI from weight and height?", 64)
sc = d.scale(140, 260, 240)
d.text(260, 490, "weight", 40, align="center")
ru = d.ruler(215, 600, 90, 300)
d.text(330, 730, "height", 40)
f = d.box(640, 440, 380, 250, "weight\n÷ height²", "grey", 40, shape="diamond")
bmi = d.box(660, 820, 340, 110, "BMI", "violet", 52, sw=3)
d.arrow(sc, f, sw=3); d.arrow(ru, f, sw=3); d.arrow(f, bmi, sw=3)
d.image(f"{IMG}/scatter_bmi.png", 1140, 230, h=760)

# ---------------------------------------------------------------- r2
d.slide("What R² means", "")
d.title("What does 0.998 mean?", 64)
d.image(f"{IMG}/r2_explainer.png", 110, 210, w=1700)
d.text(960, 900, "R² = how close the guesses are.  1.0 is perfect.", 46, align="center")

# ---------------------------------------------------------------- 4 hide it
d.slide("Now hide the formula", "Now imagine the formula lives on page 80 of a PDF,\npublished by a different organisation.\nThe columns arrive in a CSV with no recipe attached.\nSame model. Same 0.998.\nWould we spot it?\nThis is what public data looks like.")
d.title("Now hide the formula", 64)
sc = d.scale(140, 260, 240)
d.text(260, 490, "weight", 40, align="center")
ru = d.ruler(215, 600, 90, 300)
d.text(330, 730, "height", 40)
bmi = d.box(1300, 520, 340, 110, "BMI", "violet", 52, sw=3)
pdf = d.pdf_stack(720, 400, 200, 250, "p. 80")
d.arrow(sc, pdf, "grey", dashed=True); d.arrow(ru, pdf, "grey", dashed=True)
d.arrow(pdf, bmi, "grey", dashed=True)
d.text(1470, 660, "0.998", 64, VIO, align="center")
d.text(960, 900, "Would you spot it?", 64, RED, align="center")

# ---------------------------------------------------------------- 5 lab
d.slide("Then it happened to us", "[Edit] One line on the lab and the project.\nWe build models on free public data from US agencies.\nIt is good data, and anyone can check our work.")
d.title("Then it happened to us", 64)
srcs = [d.pdf_stack(130, 210 + i * 240, 110, 140, nm, n=2) for i, nm in enumerate(["CDC", "FEMA", "Census"])]
lab = d.box(640, 430, 320, 180, "our lab", "white", 48)
d.person(700, 320, 80); d.person(820, 320, 80)
m = d.box(1140, 430, 280, 180, "model", "violet", 48)
p = d.box(1560, 430, 260, 180, "score", "green", 44)
for s in srcs: d.arrow(s, lab)
d.arrow(lab, m, sw=3); d.arrow(m, p, sw=3)
d.box(640, 850, 1180, 110, "[edit: the lab + the project, one line]", "yellow", 30, dashed=True)

# ---------------------------------------------------------------- 6 score
d.slide("Our score", "This is a real run on the CDC Social Vulnerability Index.\n9,041 California neighbourhoods. Five-fold cross-validation.\nEvery dot is a neighbourhood. They all sit on the line.\nAsk the room: who would ship this?")
d.image(f"{IMG}/scatter_recipe.png", 120, 70, h=940)
d.text(1120, 380, "Our model,\non real CDC data.", 60)
d.text(1120, 600, "Almost perfect.", 72, RED)

# ---------------------------------------------------------------- 7 same shape
d.slide("Look familiar?", "Put them side by side.\nSame line. Same 0.998.\nOn the left we know the formula.\nOn the right the formula was hidden from us.\nOur CDC model had found its own BMI.")
d.title("Look familiar?", 64)
d.image(f"{IMG}/scatter_bmi.png", 140, 190, h=760)
d.image(f"{IMG}/scatter_recipe.png", 1020, 190, h=760)
d.text(520, 975, "BMI from weight and height", 32, VIO, align="center")
d.text(1400, 975, "our CDC model", 32, RED, align="center")

# ---------------------------------------------------------------- 8 the loop
d.slide("The loop", "CDC builds Theme 1 from five columns.\nWe gave our model those same five columns.\nSo the answer went in, and the answer came out.\nThe model relearned CDC's formula.\nIt told us nothing new about the world.")
d.title("The answer went in. The answer came out.", 60)
names = ["poverty", "unemployment", "housing cost", "no diploma", "no insurance"]
for i, nm in enumerate(names):
    d.box(150, 240 + i * 110, 320, 84, nm, "blue", 32)
grp = d.box(120, 220, 380, 590, None, "ink", dashed=True); grp["backgroundColor"] = "transparent"
f = d.box(800, 200, 320, 240, "CDC\nformula", "grey", 40, shape="diamond")
th = d.box(1440, 400, 340, 130, "Theme 1", "yellow", 48, sw=3)
mdl = d.box(800, 700, 320, 130, "our model", "violet", 44)
d.arrow(grp, f, sw=4, label="made from", size=30)
d.arrow(f, th, sw=4)
d.arrow(grp, mdl, "violet", sw=4, label="fed to", size=30)
d.arrow(mdl, th, "violet", sw=4, label="predicts", size=30)
d.text(960, 940, "Same five columns on both paths.", 44, RED, align="center")

# ---------------------------------------------------------------- 9 leak vs signal
d.slide("Leak vs signal", "Left: built from the target's own inputs. A thin line.\nRight: internet access. CDC ships it in the same file,\nbut it is outside the index.\nIt still relates to vulnerability. R2 is 0.384.\nThat cloud is what a real relationship looks like.")
d.title("What each one looks like", 64)
d.image(f"{IMG}/scatter_recipe.png", 140, 190, h=760)
d.image(f"{IMG}/scatter_signal.png", 1020, 190, h=760)
d.text(520, 975, "made from the target's own inputs", 32, RED, align="center")
d.text(1400, 975, "a real relationship", 32, BLUE, align="center")

# ---------------------------------------------------------------- 10 green
d.slide("Every check passed", "Nothing crashed. Cross-validation was done properly.\nThe score was great.\nThe problem sits outside the code,\nin what the data was made from.\nOur bundler would have caught a loop in our imports.\nNothing caught this one.")
d.title("Every check passed", 64)
prev = None
for i, s in enumerate(["tests", "lint", "CV", "score"]):
    b = d.box(150 + i * 420, 330, 300, 150, s, "green", 48)
    d.badge(150 + i * 420 + 240, 290, 80, "green")
    if prev: d.arrow(prev, b, sw=3)
    prev = b
d.doc(870, 600, 180, 220, None, "white")
d.text(960, 850, "the data's recipe", 36, align="center")
d.badge(1010, 570, 100, "red", "cross")
d.text(960, 940, "nobody checked", 44, RED, align="center")

# ============================================================ ACT 2: seeing the graph
# ---------------------------------------------------------------- your code too
d.slide("It's in your code too", "")
d.title("It's in your code too", 64)
cards = [("snapshot tests", "blue"), ("AI evals", "violet"), ("product metrics", "orange")]
for i, (nm, c) in enumerate(cards):
    x0 = 110 + i * 580
    d.box(x0, 200, 540, 760, None, "white", sw=2)
    d.text(x0 + 270, 230, nm, 46, align="center")
# snapshot: code -> snapshot file -> test compares to code
c1 = d.box(195, 360, 370, 100, "our code", "blue", 36)
sn = d.doc(305, 560, 150, 190, None, "white")
d.arrow(c1, sn, sw=3, label="writes", size=28)
d.curve([(470, 640), (590, 520), (560, 460)], "red", sw=3)
d.text(380, 800, "expected = actual", 34, RED, align="center")
d.text(380, 870, "can never fail", 30, GREY, align="center")
# AI evals: test questions leak into training data -> model -> 95%
tq = d.doc(745, 340, 120, 150, None, "white")
d.text(805, 500, "test questions", 26, align="center")
tr = d.box(945, 360, 220, 110, "training\ndata", "grey", 30)
d.arrow(tq, tr, "red", sw=3)
mo = d.box(860, 610, 260, 100, "model", "violet", 36)
d.arrow(tr, mo, sw=3)
d.text(960, 800, "scores 95%", 34, RED, align="center")
d.text(960, 870, "it saw the answers", 30, GREY, align="center")
# metrics: clicks -> click-through rate -> predicts clicks
ck = d.box(1395, 340, 260, 90, "clicks", "orange", 34)
ctr = d.box(1395, 500, 260, 100, "click rate", "white", 34)
pr = d.box(1395, 670, 260, 90, "predict clicks", "orange", 30)
d.arrow(ck, ctr, sw=3, label="made from", size=26); d.arrow(ctr, pr, sw=3)
d.curve([(1660, 715), (1740, 540), (1660, 385)], "red", sw=3)
d.text(1540, 800, "the answer is an input", 32, RED, align="center")
d.text(1540, 870, "same loop", 30, GREY, align="center")

# ---------------------------------------------------------------- 11 npm
d.slide("You already use one", "Every JS dev here already trusts a dependency graph.\nnpm knows that body-parser uses debug.\nThe lock file writes it down, so tools can check it.\nPublic data has no lock file.\nWe draw graphs with the source at the top, flowing down,\nlike a river.")
d.title("You already use one of these", 64)
dbg = d.box(330, 230, 240, 90, "debug", "white", 36)
bp = d.box(120, 420, 280, 90, "body-parser", "white", 34)
ex = d.box(500, 560, 240, 90, "express", "white", 36)
app = d.box(300, 760, 240, 90, "my-app", "yellow", 36)
d.arrow(dbg, bp); d.arrow(dbg, ex); d.arrow(bp, ex); d.arrow(ex, app)
d.doc(640, 740, 110, 140, None, "green")
d.text(695, 900, "package-lock.json", 26, GREEN, align="center")
acs = d.box(1260, 230, 360, 90, "ACS survey", "blue", 34)
cre = d.box(1260, 470, 360, 90, "Census estimate", "white", 34)
fema = d.box(1260, 710, 360, 90, "FEMA risk score", "yellow", 34)
d.arrow(acs, cre, "grey", label="?", size=44, dashed=True)
d.arrow(cre, fema, "grey", label="?", size=44, dashed=True)
d.doc(1700, 740, 110, 140, None, "white")
d.cross(1730, 780, 50)
d.text(1755, 900, "no lock file", 26, RED, align="center")
d.line([(960, 200), (960, 980)], "grey", sw=2, dashed=True)

# ---------------------------------------------------------------- 12 two questions
d.slide("Two questions", "Two questions we can ask about any column.\nWhere did this file come from? That is provenance.\nWhat was this number made from? That is derivation.\nMost catalogues only record the first one.")
d.title("Two questions about any column", 64)
d.box(110, 220, 800, 660, None, "white")
d.box(1010, 220, 800, 660, None, "white")
d.text(510, 250, "Where did the\nfile come from?", 46, align="center")
d.text(1410, 250, "What was the\nnumber made from?", 46, align="center")
web = d.box(200, 480, 240, 160, "website", "grey", 34)
csv = d.doc(620, 460, 160, 200, None, "blue")
d.text(700, 672, "data.csv", 30, align="center")
d.arrow(web, csv, sw=3)
i1 = d.box(1080, 450, 200, 90, "column A", "blue", 30)
i2 = d.box(1080, 600, 200, 90, "column B", "blue", 30)
ix = d.box(1520, 515, 220, 110, "index", "yellow", 36)
d.arrow(i1, ix, sw=3); d.arrow(i2, ix, sw=3)
d.pill(330, 770, "where from", "green", 34)
d.badge(640, 760, 70, "green")
d.pill(1240, 770, "made from", "red", 34)
d.text(1560, 750, "?", 72, RED)

# ---------------------------------------------------------------- 13-15 real chain (build)
d.slide("A real chain (1)", "A real example, from FEMA's own documentation.\nThe FEMA risk score. What is it made from?\nLet's walk upstream.")
d.title("What is this made from?", 64)
n = chain_base()
fade(n, ("pov", "une", "cre", "bric", "sv", "cr"))

d.slide("A real chain (2)", "First route: through a Census statistical model.\nThe unemployment rate feeds the Census estimate,\nwhich becomes FEMA's social vulnerability.")
d.title("Route 1: through a model", 64, BLUE)
n = chain_base()
for a_, b_ in (("pov", "cre"), ("une", "cre"), ("cre", "sv"), ("sv", "risk")):
    d.arrow(n[a_], n[b_], "blue", sw=4)
fade(n, ("bric", "cr"))

d.slide("A real chain (3)", "Second route: pure arithmetic, through the BRIC index.\nThe same unemployment column reaches the risk score twice.\nThree agencies are involved. Nobody owns the whole picture.")
d.title("Route 2: pure arithmetic", 64, RED)
n = chain_base()
for a_, b_ in (("pov", "cre"), ("une", "cre"), ("cre", "sv"), ("sv", "risk")):
    d.arrow(n[a_], n[b_], "blue", sw=4)
for a_, b_ in (("une", "bric"), ("bric", "cr"), ("cr", "risk")):
    d.arrow(n[a_], n[b_], "red", sw=5)
d.text(1810, 900, "one column,\ntwo routes", 44, RED, align="right")
d.text(110, 1010, "Source: FEMA National Risk Index Technical Documentation v1.20", 24, GREY)

# ---------------------------------------------------------------- 16 reading
d.slide("How to read a graph", "Boxes are datasets or columns. Arrows mean 'used to make'.\nUpstream, above the target: ancestors. What it was made from.\nDownstream, below: descendants. What was made from it.\nGrey boxes are unrelated. Those are the safe inputs.")
d.title("Reading a graph", 64)
a1 = d.box(560, 200, 240, 90, "", "red")
a2 = d.box(900, 200, 240, 90, "", "red")
t = d.box(700, 480, 300, 110, "target", "yellow", 40, sw=3)
de = d.box(730, 790, 240, 90, "", "orange")
g1 = d.box(1300, 340, 220, 90, "", "grey")
g2 = d.box(1300, 640, 220, 90, "", "grey")
d.arrow(a1, t, "red", sw=3); d.arrow(a2, t, "red", sw=3); d.arrow(t, de, "orange", sw=3)
d.arrow(g1, g2, "grey")
d.text(500, 220, "upstream", 40, RED, align="right")
d.text(680, 810, "downstream", 40, ORANGE, align="right")
d.text(1580, 470, "unrelated", 40, GREY)
d.badge(1600, 550, 70, "green")
d.line([(160, 300), (160, 840)], "ink", sw=3, arrowhead="arrow")
d.text(120, 520, "flow", 34, align="right")

# ---------------------------------------------------------------- 17 shapes
d.slide("Three shapes", "Three shapes to look for. That's all.\nUpstream of the target: stop. The target was made from it.\nDownstream: stop. It was made from the target.\nShared parent: two inputs are related to each other. Look closer.")
d.title("Three shapes to look for", 64)
for i, (head, top, bot, col) in enumerate([
        ("upstream", ("input", "blue"), ("target", "yellow"), "red"),
        ("downstream", ("target", "yellow"), ("input", "blue"), "red"),
        ("shared parent", None, None, "yellow")]):
    x0 = 110 + i * 580
    d.box(x0, 200, 540, 760, None, "white")
    d.text(x0 + 270, 230, head, 48, align="center")
    if top:
        b1 = d.box(x0 + 145, 360, 250, 100, top[0], top[1], 38)
        b2 = d.box(x0 + 145, 600, 250, 100, bot[0], bot[1], 38)
        d.arrow(b1, b2, sw=3)
    else:
        pa = d.box(x0 + 145, 360, 250, 100, "parent", "grey", 38)
        c1 = d.box(x0 + 30, 600, 220, 100, "input A", "blue", 34)
        c2 = d.box(x0 + 290, 600, 220, 100, "input B", "blue", 34)
        d.arrow(pa, c1, sw=3); d.arrow(pa, c2, sw=3)
    if col == "red":
        d.badge(x0 + 220, 780, 100, "red", "cross")
    else:
        d.warn(x0 + 215, 775, 110)

# ============================================================ ACT 3: looking after it
# ---------------------------------------------------------------- 18 write it down
d.slide("Step 1. Write it down", "Step one: write the graph down.\nA manifest is a lock file for data.\nOne entry per dataset, listing what it was made from.\nPlain YAML, kept in the repo, reviewed like code.\nThis entry comes from FEMA's documentation, section 4.1.1.")
d.title("1.  Write it down", 64)
yaml = ("FEMA_NRI.social_vulnerability:\n"
        "  measurementBasis: composite\n"
        "  derivesFrom:\n"
        "    - variable: CENSUS_CRE.social_vulnerability\n"
        "      relation: identity\n"
        "      confidence: documented")
d.box(110, 230, 1060, 340, None, "dark")
d.text(150, 270, yaml, 32, "#e9ecef", family=3)
c1 = d.box(1350, 240, 440, 110, "Census estimate", "violet", 36)
c2 = d.box(1350, 560, 440, 110, "FEMA social\nvulnerability", "white", 34)
d.arrow(c1, c2, label="identity · documented", size=28, sw=3)
d.doc(565, 680, 150, 190, None, "green")
d.text(640, 890, "a lock file for data", 36, GREEN, align="center")

# ---------------------------------------------------------------- quiz
d.slide("Spot the leak", "")
d.title("Your turn: which one is safe?", 64)
tq = d.box(760, 200, 400, 110, "FEMA risk score", "yellow", 40, sw=3)
d.text(960, 330, "we want to predict this", 30, GREY, align="center")
for i, (letter, nm) in enumerate([("A", "poverty rate"), ("B", "unemployment rate"), ("C", "rainfall")]):
    x0 = 150 + i * 560
    d.box(x0, 480, 500, 340, None, "white", sw=3)
    d.box(x0 + 190, 510, 120, 120, letter, "violet", 64, shape="ellipse")
    d.text(x0 + 250, 680, nm, 44, align="center")
d.text(960, 900, "Shout it out!", 56, RED, align="center")

# ---------------------------------------------------------------- 21 walk
d.slide("Step 2. Walk it", "Step two: walk it.\nStart at the target. Follow every arrow upstream,\nthen every arrow downstream.\nHold our input list against everything we touched.\nAnything on the path is out.")
d.title("2.  Walk it", 64)
up1 = d.box(250, 210, 240, 90, "poverty", "red", 32)
up2 = d.box(560, 210, 300, 90, "unemployment", "red", 32)
mid = d.box(380, 420, 340, 90, "Census estimate", "red", 32)
tg = d.box(390, 640, 320, 110, "risk score", "yellow", 38, sw=3)
d.box(830, 640, 220, 90, "rainfall", "grey", 32)
d.arrow(up1, mid, "red", sw=3); d.arrow(up2, mid, "red", sw=3); d.arrow(mid, tg, "red", sw=3)
d.curve([(370, 720), (170, 500), (290, 310)], "ink", sw=3, dashed=True)
d.text(140, 560, "walk\nup", 32, align="right")
d.box(1240, 210, 560, 600, None, "white")
d.doc(1270, 230, 70, 90, None, "white", lines=2)
d.text(1360, 250, "our inputs", 44)
for i, (nm, ok) in enumerate([("poverty", False), ("unemployment", False), ("rainfall", True)]):
    y = 380 + i * 130
    d.text(1300, y, nm, 44, GREEN if ok else RED)
    d.badge(1680, y - 4, 64, "green" if ok else "red", "tick" if ok else "cross")

# ---------------------------------------------------------------- 22 verdicts
d.slide("Step 3. Four answers", "Step three: get one of four answers.\nFAIL: an input sits on the target's path.\nREVIEW: two inputs share a parent. A person should look.\nPASS: the target is traced and the inputs are clear.\nUNTRACED: nobody has written down this target's lineage yet.\nWe keep UNTRACED apart on purpose.\nAn empty graph gives no answer, so it never counts as a pass.")
d.title("3.  Four answers", 64)
for i, (nm, c, mark) in enumerate([("FAIL", "red", "cross"), ("REVIEW", "yellow", "warn"),
                                   ("PASS", "green", "tick"), ("UNTRACED", "grey", "q")]):
    x0 = 110 + i * 440
    d.box(x0, 240, 400, 440, None, c, sw=3)
    if mark in ("cross", "tick"):
        d.badge(x0 + 120, 300, 160, "white" if False else c, mark)
    elif mark == "warn":
        d.warn(x0 + 120, 300, 160)
    else:
        d.box(x0 + 120, 300, 160, 160, "?", "white", 90, shape="ellipse")
    d.text(x0 + 200, 550, nm, 54, align="center")
d.text(960, 800, "no graph, no answer", 46, GREY, align="center")

# ---------------------------------------------------------------- 23 CI
d.slide("Step 4. Run it on every push", "Step four: put it in CI next to the tests.\nIt takes about a tenth of a second and needs no network.\nExit 1 means a leak. Exit 2 means the manifest is broken.\nBoth turn the build red.\nA typo in a column name fails too, because an unknown name\ncan never be cleared.")
d.title("4.  Run it on every push", 64)
gp = d.box(130, 380, 280, 120, "git push", "white", 40)
ci = d.box(560, 380, 260, 120, "CI", "white", 44)
ln = d.box(970, 380, 300, 120, "lineage\ncheck", "violet", 38)
red = d.box(1450, 250, 320, 130, None, "red")
grn = d.box(1450, 500, 320, 130, None, "green")
d.badge(1480, 270, 90, "white", "cross"); d.text(1600, 285, "leak", 48)
d.badge(1480, 520, 90, "white"); d.text(1600, 535, "clear", 48)
d.arrow(gp, ci, sw=3); d.arrow(ci, ln, sw=3); d.arrow(ln, red, "red", sw=3); d.arrow(ln, grn, "green", sw=3)
d.text(960, 820, "~0.1 seconds  ·  no network", 40, GREY, align="center")

# ---------------------------------------------------------------- 24 demo
d.slide("Demo", "Run it live:\npython3 lint_lineage.py --target FEMA_NRI.risk_score \\\n  --covariates ACS.EP_POV150 ACS.EP_UNEMP\nThen echo $? to show exit 1.\nThen misspell a column to show a typo also fails.\nIf the laptop or wifi fails, this screenshot is the real output.")
d.text(110, 70, "Live: watching it go red", 60)
d.image(f"{IMG}/terminal_fail.png", 110, 180, w=1700)

# ---------------------------------------------------------------- 25 mistake
d.slide("Where we got it wrong", "")
d.title("We got it wrong too", 64)
e8 = d.box(110, 260, 440, 120, "8 columns we\ncalled safe", "white", 38)
d.pill(600, 285, "safe", "green", 40)
d.cross(625, 280, 70)
s7 = d.box(110, 520, 440, 120, "7 of them add up\nto a score input", "red", 36)
sc_ = d.box(110, 780, 440, 110, "the score", "yellow", 44, sw=3)
d.arrow(e8, s7, sw=3); d.arrow(s7, sc_, "red", sw=4)
d.image(f"{IMG}/race_sum.png", 1060, 170, h=820)

# ---------------------------------------------------------------- 27 maintain
d.slide("Looking after the graph", "The graph only helps while it stays right.\nWe treat it like code: in the repo, reviewed in PRs.\nOur first audit found six errors in our own file,\nfour in edges we had marked certain or documented.\nSo every arrow says how sure we are,\nand every correction gets written down.")
d.title("Looking after the graph", 64)
items = [("review in PRs", "blue"), ("how sure?", "yellow"), ("log fixes", "violet"),
         ("typos fail", "red"), ("new version,\nre-check", "green")]
for i, (txt, c) in enumerate(items):
    x0 = 110 + i * 350
    d.box(x0, 300, 300, 300, None, c)
    d.text(x0 + 150, 640, txt, 38, align="center")
d.doc(195, 340, 130, 170, None, "white"); d.badge(300, 470, 70, "green")
d.arrow(d.box(480, 420, 60, 60, None, "white"), d.box(660, 420, 60, 60, None, "white"),
        color="#f08c00", sw=6, dashed=True)
for i in range(4):
    d.line([(870, 360 + i * 55), (1020, 360 + i * 55)], "grey", sw=4)
    d.tick(830, 345 + i * 55, 26, "violet")
d.box(1170, 410, 200, 70, "EP_UNEMPP", "white", 26); d.badge(1330, 360, 60, "red", "cross")
d.box(1560, 340, 160, 160, "2027", "white", 40)
d.text(960, 820, "Treat it like code.", 52, align="center")

# ---------------------------------------------------------------- 28 back to BMI
d.slide("Next time", "Back to BMI.\nNext time a score looks too good, ask:\nis this BMI from weight and height?\nThree questions to ask about any input column.\nIf we can't answer them, that column is UNTRACED.\nThat is useful to know.")
d.title("Next time a score looks too good", 64)
sc = d.scale(150, 260, 160)
ru = d.ruler(200, 480, 60, 200)
bm = d.box(400, 400, 220, 100, "BMI?", "violet", 48)
d.arrow(sc, bm, sw=3); d.arrow(ru, bm, sw=3)
for i, qq in enumerate(["What was it made from?", "Does it share a parent\nwith our target?",
                        "Who published both?"]):
    y = 240 + i * 200
    d.box(780, y, 110, 110, str(i + 1), "yellow", 52, shape="ellipse")
    d.text(930, y + (0 if "\n" in qq else 24), qq, 48)
d.text(960, 920, "Is this BMI?", 64, VIO, align="center")

# ---------------------------------------------------------------- 29 thanks
d.slide("Thank you", "Thank you.\nScan to connect on LinkedIn.\nQuestions?")
d.text(960, 90, "Thank you", 96, align="center")
d.image(f"{IMG}/qr_linkedin.png", 710, 260, w=500)
d.text(960, 800, "linkedin.com/in/kadeniyi", 44, align="center")
d.text(960, 880, "Kayode Adeniyi", 36, GREY, align="center")

d.save(OUT)
with open(OUT.replace(".excalidraw", "-notes.md"), "w") as fh:
    fh.write("# Speaker notes: The Dependency Graph Your Tests Can't See\n\n")
    fh.write("JS Monthly London #212, 12 November 2026, 8:00 to 8:45 PM.\n\n")
    for name, notes in d.notes:
        fh.write(f"## {name}\n\n{notes}\n\n")
print(d.n, "slides,", len(d.els), "elements")
