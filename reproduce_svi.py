#!/usr/bin/env python3
"""
reproduce_svi.py — check the manifest's headline R2 claims from scratch.

Downloads the CDC/ATSDR SVI 2022 California tract file and asks a gradient
booster to predict each published index from the ACS columns that index is
built from. No credentials, one HTTP request, about thirty seconds.

    pip install pandas scikit-learn
    python3 reproduce_svi.py

It also prints the adjunct analysis. The file ships 24 EP_* columns, of which
only 16 are percentile-ranked into the index. Of the other eight, seven are
race and ethnicity counts that sum exactly to EP_MINRTY, which IS Theme 3, so
they are ancestors of the index rather than bystanders. Only EP_NOINT is a
genuine co-published non-input. Treating all eight as non-inputs was the second
bug this script caught, and it is the same mistake as the first: a column's
absence from the ranking does not make it independent of the index.
"""
import io, ssl, subprocess, sys, urllib.request
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import KFold, cross_val_score

URL = "https://svi.cdc.gov/Documents/Data/2022/csv/states/California.csv"

# The 16 ranked variables, split into the four themes CDC documents. Theme
# membership is the one thing here taken from documentation rather than from
# the file, so main() asserts that these four sets partition the file's own
# EPL_* columns exactly. If a vintage changes composition the assertion fails
# loudly instead of quietly scoring the wrong variable set.
THEMES = {
    "RPL_THEME1": ["EP_POV150", "EP_UNEMP", "EP_HBURD", "EP_NOHSDP", "EP_UNINSUR"],
    "RPL_THEME2": ["EP_AGE65", "EP_AGE17", "EP_DISABL", "EP_SNGPNT", "EP_LIMENG"],
    "RPL_THEME3": ["EP_MINRTY"],
    "RPL_THEME4": ["EP_MUNIT", "EP_MOBILE", "EP_CROWD", "EP_NOVEH", "EP_GROUPQ"],
}


def fetch(url):
    """urllib first; fall back to curl, because a stock macOS Python often has
    no certificate bundle installed and the point of this script is that it
    runs anywhere without setup."""
    try:
        return urllib.request.urlopen(url, timeout=180).read()
    except (ssl.SSLError, urllib.error.URLError) as e:
        print(f"  urllib failed ({e}); retrying with curl")
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "180", url],
                           capture_output=True, check=True)
        if not r.stdout:
            raise RuntimeError("empty response")
        return r.stdout
    except Exception as e:
        sys.exit(f"download failed: {e}")


def fit(df, cols, target, label, n_iter=None):
    d = df[cols + [target]].dropna()
    model = HistGradientBoostingRegressor(random_state=0,
                                          **({"max_iter": n_iter,
                                              "learning_rate": 0.05} if n_iter else {}))
    r2 = cross_val_score(model, d[cols], d[target],
                         cv=KFold(5, shuffle=True, random_state=0),
                         scoring="r2").mean()
    print(f"  {label:<52} n={len(d):>5}  k={len(cols):>2}  R2={r2:.4f}")
    return r2


def main():
    print(f"downloading {URL}")
    raw = fetch(URL)
    df = pd.read_csv(io.BytesIO(raw), low_memory=False).replace(-999, np.nan)

    ep_all = [c for c in df.columns if c.startswith("EP_")]
    ranked = [c.replace("EPL_", "EP_") for c in df.columns if c.startswith("EPL_")]
    adjunct = [c for c in ep_all if c not in ranked]

    print(f"\n{len(df)} California tracts, "
          f"{len(ep_all)} EP_* columns delivered, "
          f"{len(ranked)} of them percentile-ranked into the index")
    print(f"adjunct (published, NOT ranked): {', '.join(adjunct)}\n")

    assert sorted(sum(THEMES.values(), [])) == sorted(ranked), (
        "theme membership does not partition the file's ranked columns")

    print("reconstructing the published indices from their own inputs:")
    for theme, cols in THEMES.items():
        n = len(cols)
        fit(df, cols, theme,
            f"{theme} <- its {n} ranked ACS input{'s' if n > 1 else ''}")
    fit(df, ranked, "RPL_THEMES", "RPL_THEMES <- the 16 ranked ACS inputs")
    fit(df, ranked, "RPL_THEMES", "RPL_THEMES <- same, longer boosting schedule", n_iter=1000)

    race = [c for c in adjunct if c != "EP_NOINT"]

    print("\nthe adjunct columns, split by what they actually are:")
    fit(df, adjunct, "RPL_THEMES", "RPL_THEMES <- all 8 adjuncts together")
    fit(df, race,    "EP_MINRTY",  f"EP_MINRTY  <- the {len(race)} race/ethnicity adjuncts")
    fit(df, race,    "RPL_THEME3", f"RPL_THEME3 <- the {len(race)} race/ethnicity adjuncts")
    fit(df, race,    "RPL_THEMES", f"RPL_THEMES <- the {len(race)} race/ethnicity adjuncts")
    fit(df, ["EP_NOINT"], "RPL_THEMES", "RPL_THEMES <- EP_NOINT alone")

    # Theme 3 has a single input, so the theme is a pure rank transform of it
    # rather than an approximation. Spearman is computed as Pearson on ranks,
    # which keeps this to pandas alone.
    d3 = df[["EP_MINRTY", "RPL_THEME3"]].dropna()
    rho = d3["EP_MINRTY"].rank().corr(d3["RPL_THEME3"].rank())
    print(f"\n  spearman(EP_MINRTY, RPL_THEME3) = {rho:.6f} "
          f"over {len(d3)} tracts")

    # The identity, checked on the raw counts rather than the rounded percents.
    e = ["E_" + c[3:] for c in race]
    d = df[e + ["E_MINRTY"]].dropna()
    diff = (d[e].sum(axis=1) - d["E_MINRTY"]).abs().max()
    print(f"  E_MINRTY - sum(the {len(race)} race/ethnicity counts): "
          f"max abs difference {diff:g} over {len(d)} tracts")
    print("\n  So seven of the eight are not bystanders at all: they sum exactly"
          "\n  to EP_MINRTY, which is the whole of Theme 3. Only EP_NOINT is a"
          "\n  genuine co-published non-input, and its R2 above is what mere"
          "\n  correlation with an index looks like. A column's absence from the"
          "\n  ranking does not make it independent of the index.")


if __name__ == "__main__":
    main()
