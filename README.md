# derives-from

I have written a dependency manifest for public statistical data, together with a
linter that reads it.

It catches one specific mistake, which is using a covariate that your prediction
target was itself built out of. Any package manager would refuse a circular
dependency of this shape without being asked to, and doing the same thing for
public data needs a dependency graph that nobody has written down yet.

---

## The problem

A great deal of public data arrives as the output of a calculation performed on
other public data.

CDC's Social Vulnerability Index is a percentile rank of four theme rankings
built from sixteen American Community Survey variables. FEMA's National Risk
Index multiplies Expected Annual Loss by a factor derived from a social
vulnerability layer and a community resilience layer, both of which reach the
ACS by their own separate routes. CDC PLACES health estimates come out of a
model whose inputs include Census demographics and an ACS poverty rate.

CDC, FEMA, and the Census Bureau all document this openly, in the methodology
documents they publish themselves.

The difficulty I keep running into is that no catalogue records any of it in a
machine readable form. Data Commons defines provenance as "the physical unit of
an import", which identifies the file a number arrived in whilst leaving the
question of what that number was computed from entirely unanswered. Those are
two separate graphs, and only one of them currently exists.

So when a model goes looking for useful covariates, nothing stops it collecting
variables that its own target was assembled from. What comes out the other end
scores extremely well, having largely recovered the formula that produced the
target in the first place.

## Why I think this is real, and how you can check

CDC ships SVI as a single CSV containing both the raw ACS inputs and the derived
index, so I handed a gradient booster those inputs and asked it to predict the
index:

```
RPL_THEME1  from its 5 Theme-1 ACS columns  ->  R2 = 0.998
RPL_THEMES  from the 16 ranked ACS columns  ->  R2 = 0.987   (0.993 tuned)
```

That covers 9,041 California tracts, cross validated, with no credentials
required and roughly thirty seconds of runtime. I quote three decimals because
the fourth moves with your library version, and these figures are stable across
scikit-learn 1.3.2 through 1.9.0 on Python 3.11, 3.12, and 3.13, checked in
clean containers. A score at that level means the
model has recovered the published arithmetic almost exactly. Run
`python3 reproduce_svi.py` and you can check it yourself, against the live CDC
file.

That script also prints the analysis that cost me the most. The delivered CSV
carries 24 `EP_*` columns, of which only 16 are ranked into the index, and I
treated the remaining eight as adjunct variables published for convenience.
Seven of them are not. The seven race and ethnicity columns sum to `E_MINRTY`
exactly, with a maximum absolute difference of zero across all 9,109 tracts, and
`EP_MINRTY` is the whole of Theme 3, so those seven are ancestors of the index
standing two hops up rather than bystanders beside it. They reconstruct
`EP_MINRTY` at R2 = 0.994 and Theme 3 at R2 = 0.992.

Only `EP_NOINT` turns out to be a genuine co-published non-input, reaching the
overall index at R2 = 0.384 on its own, which is what correlation looks like
when a variable really is beside an index rather than inside it. I had recorded
all eight as safe, which meant my own linter would clear a covariate that is a
deterministic component of the target. That is a false clearance, and a tool
that hands one out is worse than no tool. A column's absence from the ranking
does not make it independent of the index, and I have now made that mistake in
both directions.

## What this looks like in practice

I used a Google Research paper (arXiv:2608.26088) as the worked example, because
it is unusually explicit about which covariates it selected, which is exactly
what makes it possible to check. Google was plainly aware of this hazard already
and had built a rule into the pipeline to prevent it. Google's own rule reads,
verbatim:

> The covariate and target must not rely on the exact same underlying survey
> data or imputation models. Furthermore, when predicting population-related
> targets, the system restricts covariates to non-enumerative, intensive
> socioeconomic rates (e.g., Median Income) rather than enumerative counts
> (e.g., Count HousingUnit) to guarantee zero census enumeration leakage.
> (Example: Exclude Census age/income demographics if predicting a synthetic
> "Climate Vulnerability Score" derived from those same Census tables.)

The results table for FEMA Social Vulnerability, which is a synthetic
vulnerability score derived from Census tables, then lists `Count_HousingUnit`,
`Count_Person`, `Count_Household`, `HouseholderAge65OrMoreYears`, and six Census
income brackets among the eighteen covariates used.

Six of the covariates in that list map onto the ten components of the Census
Bureau's Community Resilience Estimates Social Vulnerability Measure. FEMA's
National Risk Index Technical Documentation v1.20 names that measure in section
4.1.1 as the source of its social vulnerability layer, in those words, and lists
all ten components on the same page:

| Covariate used | CRE component |
|---|---|
| `BelowPovertyLevelInThePast12Months` | Income-to-Poverty Ratio |
| `SingleMotherFamilyHousehold` | Single or zero caregiver household |
| `LimitedEnglishSpeakingHousehold` | Communication barrier |
| `HouseholderAge65OrMoreYears` | Being aged 65 years or older |
| `With0AvailableVehicles` | No vehicle access |
| `NoInternetAccess` | Households without broadband internet access |

The number that interests me there is the lift. Social Vulnerability climbs from
0.4824 on the PDFM + AEF baseline to 0.6755 once those covariates arrive, which
is far and away the largest gain in that table, whilst the Resilience Score
sitting beside it slightly declines.

Somebody reading this far can fairly object that the table above is the feature
ablation arm rather than the output of the leakage rule itself, and that the
place to look is the intelligent selection stage. I went there, and it turns out
to be the stronger version of the same point. That stage narrows Social
Vulnerability from those eighteen covariates down to three, and the score barely
moves, going from 0.6755 to 0.6773, so the three it keeps carry essentially all
of the signal. The three are `Count_Person`, `HouseholderAge65OrMoreYears`, and
`SingleMotherFamilyHousehold`. Two of them are the CRE components for being aged
65 or older and for a single or zero caregiver household, and the third is an
enumerative population count of exactly the kind the rule excludes in the same
breath as `Count HousingUnit`.

There is a second, quieter thing I noticed in the same paper. The prompt defines
`RPL_THEME1` as a five-term rank over Poverty, Unemployment,
**PerCapitaIncome**, NoHighSchoolDiploma, and Uninsured. No vintage of SVI ranks
those five together. SVI 2020 and 2022 rank five variables with housing cost
burden where per-capita income sits, and they carry no per-capita-income column
at all, whilst SVI 2018 ranks only four, being poverty, unemployment, per-capita
income, and no high school diploma. SVI 2018 does deliver an `EP_UNINSUR`
column, and it carries no `EPL_UNINSUR`, so uninsured is published in 2018
without being ranked into the index. The stated formula therefore takes
per-capita income from the 2018 vintage and uninsured from 2020 onwards, and
matches neither. Since the leakage rule quoted above keys off "the
mathematical definition of the prediction target in the prompt", a definition
that is wrong means the guard was protecting the wrong set of variables.

None of that reads to me like carelessness, because the reason it happens is
structural. Enforcing Google's rule requires knowing what the target was
computed from, and every catalogue in the pipeline is silent on exactly that
question.

---

## What is in here

**`derivation-manifest.yaml`**
60 products and 75 derivation edges, covering US and global data
infrastructure. Every edge records what it depends on and how far the evidence
lets me trust it, and every product that carries edges records that evidence
alongside them.

**`lint_lineage.py`**
Loads the manifest, walks the graph from your target in both directions, and
refuses any covariate that turns out to be an ancestor of the target or a
descendant of it, since predicting a parent from its own child leaks exactly as
completely as the reverse. It reports every derivation route it finds rather
than just the shortest one, flags covariates that are computed from each other,
flags covariates merely sharing an ancestor, and fails loudly on any name it
does not recognise, including a `coPublishedNonInputs` entry that resolves to
nothing. Before any of that it validates the manifest itself, rejecting a
cycle, an undefined reference, a missing or mistyped edge field, a duplicate
key, and any `relation`, `confidence`, or `measurementBasis` outside its
documented vocabulary, because a value this tool reads without checking is a
value that can be wrong in silence. The duplicate-key check earns its place:
YAML keeps the last of a repeated key and says nothing, so a second
`derivesFrom` on a product would delete that product's lineage on the way in,
and the linter would then clear a covariate it should have refused.

**`reproduce_svi.py`**
Downloads the live CDC SVI file and reproduces the R2 figures quoted above from
scratch, so you do not have to take any of them on trust.

**`Dockerfile`** and **`requirements.txt`**
A pinned environment, so the figures reproduce exactly rather than to whatever
your local scikit-learn happens to give. The image carries the manifest, the
two scripts, and the pinned requirements, and nothing else: no working notes,
and no source PDFs.

## Running it

```bash
pip install pyyaml pandas scikit-learn

python3 lint_lineage.py                 # audit eight real cases
python3 lint_lineage.py --graph         # print the derivation graph
python3 lint_lineage.py --target FEMA_NRI.risk_score \
                        --covariates ACS.EP_POV150 ACS.EP_UNEMP
python3 reproduce_svi.py                # verify the R2 claims from live data
```

On macOS the first thing `reproduce_svi.py` prints is usually an SSL
certificate verification failure, because a stock python.org build ships
without a certificate bundle. That line is expected, the script falls back to
curl on the line after it, and none of the figures are affected.

If you would rather install nothing, the repository ships a pinned environment:

```bash
docker build -t derives-from .
docker run --rm derives-from                            # the linter
docker run --rm --network none derives-from             # and offline, to prove it
docker run --rm derives-from python reproduce_svi.py    # the R2 figures, needs network
```

`requirements.txt` pins the exact versions the published figures were taken on,
so the container reproduces them to four decimals rather than to three.

The linter needs no API keys, no network access, and about a tenth of a second.
In `--target` mode, which is the one meant for CI, it exits 1 on FAIL, 2 on a
manifest that fails to load or fails its own validation, 2 on bad usage, and 0
otherwise, so it drops into a pipeline unchanged. An unrecognised target or
covariate name is a FAIL at exit 1 rather than a usage error, because it is
reported as a finding beside any others.

`--target` without `--covariates` is one of the usage errors. Auditing a target
against an empty covariate list once printed PASS, which is a clean bill of
health for a check that never ran, and a pipeline that loses its covariate list
to a shell expansion has to go red rather than quietly green. That was the last
shape of false clearance left in the tool, and it is the shape I would trust
least, because it is the one that shows up on a good day rather than a bad one.

The bare `lint_lineage.py` is the built-in demonstration suite rather than a
gate, and since its cases are chosen to fail it always exits 0 and reports the
tally instead.

## What it found

```
5 FAIL   1 REVIEW   1 PASS   1 UNTRACED   of 8 audited
```

The clearest failure is FEMA's composite Risk Score, which reaches the ACS down
two separate routes at the same time. This is the linter's own output, unedited:

```
 target      FEMA_NRI.risk_score  [composite]
 covariates  ACS.EP_POV150, ACS.EP_UNEMP
 verdict     FAIL   (2 error, 0 warning)

   NOTE  target is composite, not measured
         R2 against it measures reconstruction of the producing model, not agreement with reality
   ERROR ACS.EP_POV150 is an ancestor of the target (1 route)
         FEMA_NRI.risk_score -> FEMA_NRI.social_vulnerability -> CENSUS_CRE.social_vulnerability -> ACS.EP_POV150
         [component, identity, modelled_from] statistical, weakest edge: documented
   ERROR ACS.EP_UNEMP is an ancestor of the target (2 routes)
         FEMA_NRI.risk_score -> FEMA_NRI.social_vulnerability -> CENSUS_CRE.social_vulnerability -> ACS.EP_UNEMP
         [component, identity, modelled_from] statistical, weakest edge: documented
         FEMA_NRI.risk_score -> FEMA_NRI.community_resilience -> HVRI.bric -> ACS.EP_UNEMP
         [component, identity] deterministic, weakest edge: documented
```

I do not think anybody scanning a spreadsheet of column names would reliably
trace both of those routes, whilst a graph traversal finds them in milliseconds,
which is the entire reason for writing the graph down. Reporting both matters
rather more than it looks, because the two routes carry different weight, in
that one passes through a small-area model whilst the other is deterministic
arithmetic all the way down. An earlier version of my linter reported only the
shortest route, which meant it displayed whichever route happened to have fewest
hops regardless of how well evidenced it was.

The two quiet cases carry as much weight for me as the failures do. A checker
raising an alarm on every input it received would be worthless, so the suite
includes one target with a fully traced lineage whose covariates are genuinely
unrelated to it, and that comes back `PASS` with zero findings. It also
separates that from `UNTRACED`, which is what death-certificate mortality
returns, because the registry has no recorded ancestors, so there was never
anything for the traversal to find, and calling that a pass would have been
flattering the tool rather than testing it.

---

## Reading the manifest

Every product carries a `measurementBasis`:

| value | count | meaning |
|---|---|---|
| `measured` | 39 | direct enumeration, survey, sensor, or registry |
| `modelled` | 9 | output of a statistical or machine learning model |
| `composite` | 12 | deterministic arithmetic over other published products |

This field carries a surprising amount of weight on its own. Nothing in any
public catalogue currently distinguishes a census count from a random forest
prediction, so every downstream user ends up treating the two as the same kind
of number.

Every edge carries a `relation`:

| value | count | meaning |
|---|---|---|
| `component` | 42 | A is a mathematical ingredient of B |
| `modelled_from` | 28 | A is a covariate in the model that produces B |
| `identity` | 2 | B is A, republished under a different name |
| `poststratified_on` | 2 | A supplies the population weights B is raked to |
| `denominator` | 1 | A is the denominator when B is expressed as a rate |

And a `confidence`:

| value | count | meaning |
|---|---|---|
| `certain` | 30 | formula published, or inputs and outputs ship in the same file |
| `documented` | 41 | stated in the publishing agency's own methodology, CDC's, FEMA's, HVRI's, the WFP's, and so on |
| `inferred` | 4 | strongly implied without being verbatim, treat as provisional |

I made confidence a first class field deliberately, because a lineage graph that
nobody had audited would recreate the exact problem it exists to solve.

One product also carries `coPublishedNonInputs`, which lists variables shipped
in the same file as the index whilst taking no part in computing it. That field
exists because of the bug I described above, and its purpose is to stop a future
reader re-adding an edge that has already been removed once.

## What I am not claiming

I am making no claim that any published result is wrong, since per target
feature lists and fold structures are usually unavailable. My claim concerns
what a benchmark is capable of distinguishing, and it says nothing whatsoever
about anyone's competence or intent.

It is also incomplete, covering 60 products against an estimated 400 or more
official composite indices worldwide, and four edges remain marked `inferred`.
I would expect rather more of it to be wrong than my own confidence labels
suggest, given that only the edges I actually checked are known either way, and
given that the first audit of this file found six errors, four of them in edges
I had already labelled `certain` or `documented`.

The honest version of this work is generated by CDC, FEMA, and the Census Bureau
themselves, out of the methodology documents they already publish, because they
are the people best placed to do it and they currently have no schema to record
it in. That last part is the piece I think Data Commons is well placed to fix,
since two new fields on the statistical variable schema, `derivesFrom` and
`measurementBasis`, would give every producer somewhere to put what they already
know.

## Sources

* CDC/ATSDR Social Vulnerability Index, <https://svi.cdc.gov/>
* CDC PLACES methodology, Prev Chronic Dis 2022, <https://www.cdc.gov/pcd/issues/2022/21_0459.htm>
* FEMA National Risk Index Technical Documentation v1.20, December 2025, <https://www.fema.gov/sites/default/files/documents/fema_national-risk-index_technical-documentation.pdf>
* Census Community Resilience Estimates, <https://www.census.gov/programs-surveys/community-resilience-estimates.html>
* HVRI BRIC, University of South Carolina
* WorldPop methods, <https://www.worldpop.org/methods/>
* AlphaEarth Foundations, <https://arxiv.org/abs/2507.22291>
* HungerMap LIVE methods, Foini et al., Commun Earth Environ 2024, <https://www.nature.com/articles/s43247-024-01698-9>
* Kummu et al., gridded GDP, Sci Data 2018, <https://www.nature.com/articles/sdata20184>
* English Indices of Deprivation 2019, <https://www.gov.uk/government/statistics/english-indices-of-deprivation-2019>
* Data Commons data model, <https://docs.datacommons.org/data_model.html>
* Paper used as the worked example, <https://arxiv.org/abs/2608.26088>

## Licence

The manifest and the linter are released under CC0, and the upstream datasets
keep their own terms.
