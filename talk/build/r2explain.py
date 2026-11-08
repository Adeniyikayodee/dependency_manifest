import sys, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT = sys.argv[1]
plt.rcParams.update({"font.family": "Arial", "font.size": 20, "axes.spines.top": False, "axes.spines.right": False})
r = np.random.default_rng(1); x = r.uniform(0, 1, 600)
panels = [(0.01, "#2f9e44", "R² ≈ 1.0", "spot on"),
          (0.29, "#f08c00", "R² ≈ 0.5", "rough idea"),
          (None, "#e03131", "R² ≈ 0", "no idea")]
fig, axs = plt.subplots(1, 3, figsize=(18, 6.5), dpi=150)
for ax, (noise, c, t, sub) in zip(axs, panels):
    y = r.uniform(0, 1, 600) if noise is None else x + r.normal(0, noise, 600)
    ax.scatter(x, y, s=10, alpha=.5, color=c, linewidths=0)
    ax.plot([0, 1], [0, 1], color="#1e1e1e", lw=1.5, ls="--")
    ax.set(xlim=(0, 1), ylim=(-.2, 1.2), xticks=[], yticks=[])
    ax.set_xlabel("real answer"); ax.set_ylabel("model's guess")
    ax.set_title(t, fontsize=34, weight="bold", color=c, pad=12)
    ax.text(.5, -.18, sub, transform=ax.transAxes, ha="center", fontsize=28, color="#1e1e1e")
fig.tight_layout(); fig.subplots_adjust(bottom=.18)
fig.savefig(f"{OUT}/r2_explainer.png", facecolor="white")
