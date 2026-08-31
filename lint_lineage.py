#!/usr/bin/env python3
"""
lint_lineage.py — refuse covariates that are ancestors of your own target.

The check every package manager performs and no data catalogue does.

    python3 lint_lineage.py                 # audit the built-in real cases
    python3 lint_lineage.py --graph         # print the derivation graph
    python3 lint_lineage.py --target X --covariates A B C

Reads derivation-manifest.yaml (schema derives-from/0.2).

Names are checked against the manifest before anything else. An unrecognised
target or covariate is a hard failure, never a quiet pass: a linter that
returns a clean bill of health on a typo is worse than no linter.
"""
import argparse, sys
from collections import deque
from itertools import combinations
import yaml

MANIFEST = "derivation-manifest.yaml"

# A route is only as good as its weakest edge.
CONF_RANK = {"certain": 3, "documented": 2, "inferred": 1, "unstated": 0}
# Relations that compose deterministically: the target is arithmetic over the
# covariate, so fitting a model on it recovers a published formula.
DETERMINISTIC = {"component", "identity", "denominator"}
# The closed vocabularies. Both are looked up in tables above and below, so an
# unrecognised value would quietly downgrade a route to "statistical" or to
# zero confidence instead of announcing itself.
RELATIONS = {"component", "modelled_from", "identity",
             "poststratified_on", "denominator"}
BASES = {"measured", "modelled", "composite"}


def _die(msg):
    """The single exit for a manifest this tool cannot trust. Always 2, never
    1: exit 1 is reserved for "lineage violation found", and a pipeline has to
    be able to tell a broken manifest from a real leak."""
    print(msg, file=sys.stderr)
    sys.exit(2)


class _StrictLoader(yaml.SafeLoader):
    """SafeLoader that refuses duplicate keys.

    PyYAML keeps the last of a duplicate key and says nothing about it. In a
    hand-edited manifest of this size that is a live hazard: a second
    `derivesFrom` on a product silently deletes every edge the first one
    held, the traversal then finds no route from target to covariate, and the
    linter clears a covariate it should have refused. That is a false
    clearance arriving through the parser rather than through the data, which
    makes it the hardest kind to notice, so it is refused here instead."""


def _no_duplicate_keys(loader, node, deep=False):
    seen = {}
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        line = key_node.start_mark.line + 1
        if key in seen:
            _die(f"manifest: duplicate key {key!r} at line {line}, already "
                 f"defined at line {seen[key]}; YAML would keep only the "
                 f"last, silently discarding the first")
        seen[key] = line
    return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)


_StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicate_keys)


# --------------------------------------------------------------- graph model
class Lineage:
    def __init__(self, path=MANIFEST):
        self.p = self._load(path)
        for k, v in self.p.items():
            self._check_product(k, v)
        self.edges = {k: self._read_edges(k, v) for k, v in self.p.items()}
        self.copub = {k: list(v.get("coPublishedNonInputs") or [])
                      for k, v in self.p.items()}

    @staticmethod
    def _load(path):
        """Every way a manifest can be unusable exits 2, matching the documented
        contract. Without this an unreadable file exits 1 with a traceback, which
        is the code CI uses for 'lineage violation found'."""
        try:
            with open(path) as fh:
                doc = yaml.load(fh, _StrictLoader)
        except OSError as e:
            _die(f"manifest unreadable: {e}")
        except yaml.YAMLError as e:
            _die(f"manifest is not valid YAML: {e}")
        if not isinstance(doc, dict) or not isinstance(doc.get("products"), dict):
            _die(f"manifest has no top-level 'products' mapping: {path}")
        return doc["products"]

    @staticmethod
    def _check_product(name, prod):
        """Products are validated before anything walks them, because a field
        this tool reads without checking is a field that can be wrong in
        silence, which is the failure this whole manifest exists to argue
        against."""
        if not isinstance(prod, dict):
            _die(f"manifest: product {name!r} is {type(prod).__name__}, "
                 f"expected a mapping")
        basis = prod.get("measurementBasis")
        if basis not in BASES:
            _die(f"manifest: product {name!r} has measurementBasis {basis!r}; "
                 f"expected one of {', '.join(sorted(BASES))}")
        cop = prod.get("coPublishedNonInputs")
        if cop is not None and (not isinstance(cop, list)
                                or not all(isinstance(c, str) for c in cop)):
            _die(f"manifest: product {name!r} has a coPublishedNonInputs that "
                 f"is not a list of product names")

    @staticmethod
    def _read_edges(name, prod):
        """Edges are read field by field rather than by direct subscript. A
        mistyped key used to raise KeyError and exit 1, so a typo in the
        manifest was indistinguishable from the leak this tool reports."""
        raw = prod.get("derivesFrom") or []
        if not isinstance(raw, list):
            _die(f"manifest: {name}.derivesFrom is {type(raw).__name__}, "
                 f"expected a list")
        out = []
        for i, e in enumerate(raw):
            at = f"{name}.derivesFrom[{i}]"
            if not isinstance(e, dict):
                _die(f"manifest: {at} is {type(e).__name__}, expected a mapping")
            missing = [f for f in ("variable", "relation") if not e.get(f)]
            if missing:
                _die(f"manifest: {at} is missing {', '.join(missing)}; "
                     f"its keys are {', '.join(sorted(e)) or '(none)'}")
            if e["relation"] not in RELATIONS:
                _die(f"manifest: {at} has relation {e['relation']!r}; "
                     f"expected one of {', '.join(sorted(RELATIONS))}")
            conf = e.get("confidence", "unstated")
            if conf not in CONF_RANK:
                _die(f"manifest: {at} has confidence {conf!r}; "
                     f"expected one of {', '.join(sorted(CONF_RANK))}")
            out.append((e["variable"], e["relation"], conf))
        return out

    def basis(self, n):  return self.p.get(n, {}).get("measurementBasis", "unknown")
    def label(self, n):  return self.p.get(n, {}).get("label", n)
    def known(self, n):  return n in self.p

    def dangling(self):
        """Any reference the manifest never defines, from either field.
        coPublishedNonInputs is checked too: an entry that resolves to nothing
        silently disables the near-miss note it exists to raise, which is the
        same class of invisible gap this whole manifest is written against."""
        named = {v for es in self.edges.values() for v, _, _ in es}
        named |= {c for cs in self.copub.values() for c in cs}
        return sorted(named - set(self.p))

    def ancestors(self, node):
        """Every product `node` was transitively computed from."""
        seen, q = set(), deque([node])
        while q:
            for v, _, _ in self.edges.get(q.popleft(), []):
                if v not in seen:
                    seen.add(v); q.append(v)
        return seen

    def routes(self, frm, to, _acc=None):
        """EVERY distinct derivation route frm -> ... -> to, not just the
        shortest. A shortest-path search reports whichever route happens to
        have fewest hops, which is often the one resting on the weakest
        evidence. Enumerating them all lets the caller rank by confidence."""
        _acc = _acc or [frm]
        out = []
        for v, rel, conf in self.edges.get(frm, []):
            step = (frm, rel, conf, v)
            if v == to:
                out.append([step])
            elif v not in _acc:
                for tail in self.routes(v, to, _acc + [v]):
                    out.append([step] + tail)
        return out

    @staticmethod
    def strength(route):
        """Confidence of a route is the confidence of its weakest edge."""
        return min(CONF_RANK.get(s[2], 0) for s in route)

    @staticmethod
    def render(route):
        chain = " -> ".join([route[0][0]] + [s[3] for s in route])
        rels = ", ".join(dict.fromkeys(s[1] for s in route))
        conf = min(route, key=lambda s: CONF_RANK.get(s[2], 0))[2]
        return chain, rels, conf

    def find_cycles(self):
        """A well-formed manifest is a DAG. Report any back-edge."""
        WHITE, GREY, BLACK = 0, 1, 2
        color, out = {n: WHITE for n in self.p}, []
        def dfs(n, stack):
            color[n] = GREY; stack.append(n)
            for v, _, _ in self.edges.get(n, []):
                if color.get(v) == GREY:
                    out.append(stack[stack.index(v):] + [v])
                elif color.get(v) == WHITE:
                    dfs(v, stack)
            stack.pop(); color[n] = BLACK
        for n in self.p:
            if color[n] == WHITE: dfs(n, [])
        return out


# ------------------------------------------------------------------- the lint
def audit(g, target, covariates):
    findings = []

    # ---- name resolution first. An unknown name is a failure, not a pass.
    if not g.known(target):
        findings.append(("ERROR", f"target {target!r} is not in the manifest",
                         "cannot audit an unknown target; check the spelling or add the product"))
    for c in covariates:
        if not g.known(c):
            findings.append(("ERROR", f"covariate {c!r} is not in the manifest",
                             "an unrecognised covariate cannot be cleared; check the spelling"))
    if any(s == "ERROR" for s, _, _ in findings):
        return findings, False

    anc = g.ancestors(target)
    traced = bool(anc)

    if g.basis(target) in ("modelled", "composite"):
        findings.append(("NOTE", f"target is {g.basis(target)}, not measured",
                         "R2 against it measures reconstruction of the producing "
                         "model, not agreement with reality"))
    if not traced:
        findings.append(("NOTE", "target has no recorded lineage",
                         "nothing upstream to check against; a pass here means "
                         "'not yet traced', not 'verified independent'"))

    # ---- covariate is an ancestor of the target
    for c in covariates:
        if c == target:
            findings.append(("ERROR", f"{c} IS the target", "")); continue

        if c in g.copub.get(target, []):
            findings.append(("NOTE", f"{c} is co-published with the target",
                             "ships in the same file and is NOT an input; safe to "
                             "use, and the reason this manifest records near-misses"))

        if c != target and target in g.ancestors(c):
            # The covariate was computed FROM the target. Predicting a parent
            # from its own child leaks just as completely as the reverse, and
            # it is the direction a causal-direction filter is meant to catch.
            rs = sorted(g.routes(c, target), key=g.strength, reverse=True)
            detail = []
            for r in rs:
                chain, rels, conf = g.render(r)
                kind = "deterministic" if all(s[1] in DETERMINISTIC for s in r) else "statistical"
                detail.append(f"{chain}\n[{rels}] {kind}, weakest edge: {conf}")
            findings.append(("ERROR", f"{c} is a descendant of the target "
                                      f"({len(rs)} route{'s' if len(rs) > 1 else ''})",
                             "\n".join(detail)))

        if c in anc:
            # Being an ancestor is the failure condition, whatever the route.
            # Whether the composition is arithmetic or statistical changes how
            # completely the leak reconstructs the target, not whether it is a
            # leak; that nuance is reported per route rather than discounted
            # into a warning. Severity gradients are how leaks survive review.
            rs = sorted(g.routes(target, c), key=g.strength, reverse=True)
            detail = []
            for r in rs:
                chain, rels, conf = g.render(r)
                kind = "deterministic" if all(s[1] in DETERMINISTIC for s in r) else "statistical"
                detail.append(f"{chain}\n[{rels}] {kind}, weakest edge: {conf}")
            findings.append(("ERROR", f"{c} is an ancestor of the target "
                                      f"({len(rs)} route{'s' if len(rs) > 1 else ''})",
                             "\n".join(detail)))

    # ---- covariates against each other
    for a, b in combinations([c for c in covariates if g.known(c)], 2):
        if b in g.ancestors(a) or a in g.ancestors(b):
            parent, child = (b, a) if b in g.ancestors(a) else (a, b)
            findings.append(("ERROR", f"{child} is computed from {parent}",
                             "these two covariates are not independent of each "
                             "other; the pair is collinear by construction"))
        else:
            shared = g.ancestors(a) & g.ancestors(b)
            if shared:
                findings.append(("WARN", f"{a} and {b} share ancestry",
                                 "common: " + ", ".join(sorted(shared))))
    return findings, traced


# ------------------------------------------------------------------ reporting
BAR = "─" * 78
def report(g, name, target, covariates):
    f, traced = audit(g, target, covariates)
    errs = sum(1 for s, _, _ in f if s == "ERROR")
    warns = sum(1 for s, _, _ in f if s == "WARN")
    if errs:
        verdict = "FAIL"
    elif warns:
        verdict = "REVIEW"
    else:
        verdict = "PASS" if traced else "UNTRACED"
    print(f"\n{BAR}\n {name}\n{BAR}")
    print(f" target      {target}  [{g.basis(target)}]")
    print(f" covariates  {', '.join(covariates) or '(none)'}")
    print(f" verdict     {verdict}   ({errs} error, {warns} warning)\n")
    for sev, msg, detail in f:
        print(f"   {sev:<5} {msg}")
        for line in detail.split("\n"):
            if line.strip():
                print(f"         {line.strip()}")
    return verdict


CASES = [
    ("FEMA Social Vulnerability from ACS covariates",
     "FEMA_NRI.social_vulnerability",
     ["ACS.EP_POV150", "ACS.EP_NOVEH", "ACS.EP_NOINT"]),
    ("FEMA composite Risk Score from ACS covariates",
     "FEMA_NRI.risk_score",
     ["ACS.EP_POV150", "ACS.EP_UNEMP"]),
    ("CDC PLACES tract health from ACS demographics",
     "CDC_PLACES.tract",
     ["ACS.EP_POV150", "ACS.EP_AGE65"]),
    ("Nigeria food security: HungerMap beside its own inputs",
     "HUNGERMAP.live",
     ["SAT.viirs_ntl", "SAT.modis_ndvi", "WORLDBANK.food_prices"]),
    ("Fusing AlphaEarth and WorldPop as independent modalities",
     "CDC_PLACES.tract",
     ["ALPHAEARTH.embeddings", "WORLDPOP.gridded_population"]),
    ("An SVI theme beside the ACS column it is built from",
     "NVSS.mortality",
     ["CDC_SVI.RPL_THEME1", "ACS.EP_POV150"]),
    ("Control: traced target, unrelated covariates",
     "CDC_PLACES.tract",
     ["SAT.chirps_rainfall", "SAT.palsar2"]),
    ("Control: mortality registry from satellite embeddings",
     "NVSS.mortality",
     ["ALPHAEARTH.embeddings"]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=MANIFEST)
    ap.add_argument("--target"); ap.add_argument("--covariates", nargs="*")
    ap.add_argument("--graph", action="store_true")
    a = ap.parse_args()

    # Usage is settled before the manifest is touched, so a usage error can
    # never be interleaved with a report. Both directions are errors. Passing
    # --covariates without --target leaves nothing to audit against, and
    # --target without --covariates used to print PASS on an empty covariate
    # list: a clean bill of health for a check that never ran. A CI job whose
    # covariate list is lost to a shell expansion has to go red, not green.
    if a.covariates and not a.target:
        ap.error("--covariates requires --target")
    if a.target and not a.covariates and not a.graph:
        ap.error("--target requires --covariates; auditing a target against an "
                 "empty covariate list would report PASS, which is a clearance "
                 "for something nothing was checked against")

    g = Lineage(a.manifest)

    print(f"derives-from linter · {len(g.p)} products · "
          f"{sum(len(v) for v in g.edges.values())} derivation edges")
    cyc, dang = g.find_cycles(), g.dangling()
    if cyc or dang:
        print("manifest self-check: FAILED")
        for c in cyc:
            print(f"   CYCLE                {' -> '.join(c)}")
        for d in dang:
            print(f"   UNDEFINED REFERENCE  {d}")
        sys.exit(2)
    print("manifest self-check: DAG, no back-edges")

    if a.graph:
        for n in sorted(g.p):
            if g.edges[n] or g.copub[n]:
                print(f"\n{n}  [{g.basis(n)}]")
                for v, rel, conf in g.edges[n]:
                    print(f"    <- {v:<34} {rel:<18} {conf}")
                for v in g.copub[n]:
                    print(f"    ." + f". {v:<33} co-published, NOT an input")
        return

    if a.target:
        v = report(g, "custom", a.target, a.covariates or [])
        sys.exit(1 if v == "FAIL" else 0)

    verdicts = [report(g, *c) for c in CASES]
    print(f"\n{BAR}")
    print(f" {verdicts.count('FAIL')} FAIL   {verdicts.count('REVIEW')} REVIEW   "
          f"{verdicts.count('PASS')} PASS   {verdicts.count('UNTRACED')} UNTRACED"
          f"   of {len(CASES)} audited")
    print(BAR)


if __name__ == "__main__":
    main()
