"""Real charts for the talk, from the live CDC SVI 2022 California file."""
import sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.metrics import r2_score

CSV, OUT = sys.argv[1], sys.argv[2]
INK, RED, BLUE, GREEN, GREY = "#1e1e1e", "#e03131", "#1971c2", "#2f9e44", "#adb5bd"
plt.rcParams.update({"font.family": "Arial", "font.size": 20,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": INK, "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK})

df = pd.read_csv(CSV, low_memory=False).replace(-999, np.nan)
T1 = ["EP_POV150", "EP_UNEMP", "EP_HBURD", "EP_NOHSDP", "EP_UNINSUR"]
T2 = ["EP_AGE65", "EP_AGE17", "EP_DISABL", "EP_SNGPNT", "EP_LIMENG"]
T4 = ["EP_MUNIT", "EP_MOBILE", "EP_CROWD", "EP_NOVEH", "EP_GROUPQ"]
ALL16 = T1 + T2 + ["EP_MINRTY"] + T4
ranked = {c.replace("EPL_", "EP_") for c in df.columns if c.startswith("EPL_")}
adj = [c for c in df.columns if c.startswith("EP_") and c not in ranked]
RACE = [c for c in adj if c != "EP_NOINT"]
cv = KFold(5, shuffle=True, random_state=0)


def pred(cols, target):
    d = df[cols + [target]].dropna()
    p = cross_val_predict(HistGradientBoostingRegressor(random_state=0),
                          d[cols], d[target], cv=cv)
    return d[target].values, p, r2_score(d[target], p)


def scatter(cols, target, colour, title, fname):
    y, p, r2 = pred(cols, target)
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    ax.scatter(y, p, s=4, alpha=.35, color=colour, linewidths=0)
    ax.plot([0, 1], [0, 1], color=INK, lw=1.5, ls="--")
    ax.set(xlim=(0, 1), ylim=(-.05, 1.05), xticks=[0, .5, 1], yticks=[0, .5, 1])
    ax.set_xlabel("published by CDC")
    ax.set_ylabel("model's guess")
    ax.set_title(title, fontsize=22, pad=14, color=INK)
    ax.text(.04, .93, f"R² = {r2:.3f}", transform=ax.transAxes,
            fontsize=34, weight="bold", color=colour)
    ax.text(.04, .86, f"{len(y):,} California tracts", transform=ax.transAxes,
            fontsize=16, color="#495057")
    fig.tight_layout(); fig.savefig(f"{OUT}/{fname}", facecolor="white"); plt.close(fig)
    print(fname, round(r2, 4), len(y))
    return r2


r_recipe = scatter(T1, "RPL_THEME1", RED, "Theme 1, from its own 5 inputs", "scatter_recipe.png")
r_signal = scatter(["EP_NOINT"], "RPL_THEMES", BLUE, "Overall index, from internet access", "scatter_signal.png")

rows = [
    ("Theme 3  ←  its 1 input", ["EP_MINRTY"], "RPL_THEME3", RED),
    ("Theme 1  ←  its 5 inputs", T1, "RPL_THEME1", RED),
    ("Theme 4  ←  its 5 inputs", T4, "RPL_THEME4", RED),
    ("Theme 2  ←  its 5 inputs", T2, "RPL_THEME2", RED),
    ("Theme 3  ←  7 race columns", RACE, "RPL_THEME3", RED),
    ("Index  ←  its 16 inputs", ALL16, "RPL_THEMES", RED),
    ("Index  ←  internet access", ["EP_NOINT"], "RPL_THEMES", BLUE),
]
vals = []
for label, cols, t, c in rows:
    vals.append(pred(cols, t)[2]); print(label, round(vals[-1], 4))
fig, ax = plt.subplots(figsize=(13, 7), dpi=150)
ys = np.arange(len(rows))[::-1]
ax.barh(ys, vals, color=[r[3] for r in rows], height=.62)
for yv, v in zip(ys, vals):
    ax.text(v + .015, yv, f"{v:.3f}", va="center", fontsize=20, color=INK)
ax.set_yticks(ys, [r[0] for r in rows], fontsize=19)
ax.set_xlim(0, 1.12); ax.set_xticks([0, .5, 1])
ax.set_xlabel("R²  (5-fold cross-validated)")
ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
fig.tight_layout(); fig.savefig(f"{OUT}/r2_bars.png", facecolor="white"); plt.close(fig)

# The identity behind the mistake: 7 race counts add up to E_MINRTY.
e = ["E_" + c[3:] for c in RACE]
d = df[e + ["E_MINRTY"]].dropna()
s = d[e].sum(axis=1)
print("race identity max diff", (s - d["E_MINRTY"]).abs().max(), len(d))
fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
ax.scatter(d["E_MINRTY"], s, s=5, alpha=.4, color=RED, linewidths=0)
m = d["E_MINRTY"].max()
ax.plot([0, m], [0, m], color=INK, lw=1.5, ls="--")
ax.set_xlabel("E_MINRTY (published)")
ax.set_ylabel("sum of the 7 race columns")
ax.set_title("They add up exactly", fontsize=22, pad=14)
ax.text(.04, .9, f"max difference: {(s - d['E_MINRTY']).abs().max():g}",
        transform=ax.transAxes, fontsize=24, weight="bold", color=RED)
ax.text(.04, .83, f"{len(d):,} tracts", transform=ax.transAxes, fontsize=16, color="#495057")
fig.tight_layout(); fig.savefig(f"{OUT}/race_sum.png", facecolor="white"); plt.close(fig)
