import sys, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.metrics import r2_score
OUT = sys.argv[1]
INK, VIO = "#1e1e1e", "#6741d9"
plt.rcParams.update({"font.family": "Arial", "font.size": 20, "axes.spines.top": False, "axes.spines.right": False})
r = np.random.default_rng(0); n = 9000
h = r.normal(1.70, .10, n); w = r.normal(75, 15, n).clip(40, 150)
bmi = w / h**2
X = np.c_[h, w]
p = cross_val_predict(HistGradientBoostingRegressor(random_state=0), X, bmi, cv=KFold(5, shuffle=True, random_state=0))
r2 = r2_score(bmi, p); print(r2)
fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
ax.scatter(bmi, p, s=4, alpha=.35, color=VIO, linewidths=0)
lo, hi = 12, 50
ax.plot([lo, hi], [lo, hi], color=INK, lw=1.5, ls="--")
ax.set(xlim=(lo, hi), ylim=(lo, hi), xticks=[20, 30, 40], yticks=[20, 30, 40])
ax.set_xlabel("real BMI"); ax.set_ylabel("model's guess")
ax.set_title("BMI, from height and weight", fontsize=22, pad=14)
ax.text(.04, .93, f"R² = {r2:.3f}", transform=ax.transAxes, fontsize=34, weight="bold", color=VIO)
ax.text(.04, .86, "9,000 simulated people", transform=ax.transAxes, fontsize=16, color="#495057")
fig.tight_layout(); fig.savefig(f"{OUT}/scatter_bmi.png", facecolor="white")
