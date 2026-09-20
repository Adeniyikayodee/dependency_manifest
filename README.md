# derives-from

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22274757.svg)](https://doi.org/10.5281/zenodo.22274757)

A dependency manifest for public statistical data, and a linter that reads it.

It catches one mistake: using a covariate that your prediction target was built
out of. A package manager refuses a circular dependency without being asked.
Public data has no dependency graph, so nobody catches the same thing here.

---

## The problem

A lot of public data is calculated from other public data.

* CDC's Social Vulnerability Index (SVI) is built from sixteen American
  Community Survey (ACS) variables.
* FEMA's National Risk Index multiplies expected losses by a social
  vulnerability layer and a community resilience layer. Both of those trace
  back to the ACS by separate routes.
* CDC PLACES health estimates come from a model fed Census demographics and an
  ACS poverty rate.

The agencies document all of this themselves. What nobody has written down is a
machine-readable version of it. Data Commons records which file a number arrived
in, not what the number was computed from. Those are two different graphs, and
only one of them exists.

So when a model goes shopping for covariates, nothing stops it picking up
variables its own target was assembled from. The model then scores brilliantly,
because it has rediscovered the formula that made the target.

## You can check this yourself

CDC ships SVI as one CSV holding both the raw ACS inputs and the finished index.
I handed a gradient booster those inputs and asked it to predict the index:

```
RPL_THEME1  from its 5 Theme-1 ACS columns  ->  R2 = 0.998
RPL_THEMES  from the 16 ranked ACS columns  ->  R2 = 0.987   (0.993 tuned)
```

That is 9,041 California tracts, cross-validated, no credentials, about thirty
seconds. A score that high means the model has recovered the published
arithmetic almost exactly. Run `python3 reproduce_svi.py` and watch it happen
against the live CDC file. I quote three decimals because the fourth moves with
your library version; these hold across scikit-learn 1.3.2 to 1.9.0 on Python
3.11, 3.12 and 3.13.

The same script prints the mistake that cost me the most. The CSV carries 24
`EP_*` columns and only 16 are ranked into the index. I assumed the other eight
were just published alongside it. Seven of them were not. Those seven race and
ethnicity columns add up exactly to `E_MINRTY`, and `EP_MINRTY` is the whole of
Theme 3, so they sit two hops above the index rather than beside it. They rebuild
`EP_MINRTY` at R2 = 0.994 and Theme 3 at R2 = 0.992.

Only `EP_NOINT` is genuinely beside the index, reaching it at R2 = 0.384 on its
own. I had logged all eight as safe, which means my own linter would have waved
through a column the target is made of. A tool that hands out a false all-clear
is worse than no tool. Missing from the ranking does not mean independent of the
index, and I have now got that wrong in both directions.

## What this looks like in the wild

I used a Google Research paper (arXiv:2608.26088) as the worked example, because
it says exactly which covariates it used, which is what makes checking possible.
Google knew about this hazard and wrote a rule against it:

> The covariate and target must not rely on the exact same underlying survey
> data or imputation models. Furthermore, when predicting population-related
> targets, the system restricts covariates to non-enumerative, intensive
> socioeconomic rates (e.g., Median Income) rather than enumerative counts
> (e.g., Count HousingUnit) to guarantee zero census enumeration leakage.

The results table for FEMA Social Vulnerability then lists `Count_HousingUnit`,
`Count_Person`, `Count_Household`, `HouseholderAge65OrMoreYears` and six Census
income brackets among its eighteen covariates.

Six of those covariates map onto the Census Bureau's Community Resilience
Estimates (CRE) Social Vulnerability Measure. FEMA's National Risk Index
Technical Documentation v1.20 names that measure in section 4.1.1 as the source
of its social vulnerability layer:

| Covariate used | CRE component |
|---|---|
| `BelowPovertyLevelInThePast12Months` | Income-to-Poverty Ratio |
| `SingleMotherFamilyHousehold` | Single or zero caregiver household |
| `LimitedEnglishSpeakingHousehold` | Communication barrier |
| `HouseholderAge65OrMoreYears` | Being aged 65 years or older |
| `With0AvailableVehicles` | No vehicle access |
| `NoInternetAccess` | Households without broadband internet access |

Social Vulnerability jumps from 0.4824 to 0.6755 once those covariates arrive,
by far the biggest gain in the table, while the Resilience Score next to it
slightly drops.

You could fairly say that table is the ablation arm, not the leakage rule doing
its job, and that the selection stage is the place to look. I looked, and it
makes the point harder. That stage cuts Social Vulnerability from eighteen
covariates to three and the score barely moves, 0.6755 to 0.6773, so those three
carry nearly all the signal. They are `Count_Person`,
`HouseholderAge65OrMoreYears` and `SingleMotherFamilyHousehold`. Two are CRE
components. The third is exactly the kind of enumerative count the rule names.

There is a quieter problem in the same paper. Its prompt defines `RPL_THEME1` as
a rank over Poverty, Unemployment, **PerCapitaIncome**, NoHighSchoolDiploma and
Uninsured. No vintage of SVI ranks those five together. SVI 2020 and 2022 use
housing cost burden where per-capita income sits, and ship no per-capita-income
column at all. SVI 2018 ranks only four and has no `EPL_UNINSUR`. So the stated
formula takes per-capita income from one vintage and uninsured from another, and
matches neither. The leakage rule keys off that definition, so a wrong definition
means the guard protected the wrong variables.

None of this reads as carelessness to me. Enforcing Google's rule means knowing
what the target was computed from, and every catalogue in the pipeline is silent
on that.

---

## What is in here

**`derivation-manifest.yaml`** - 60 products and 75 derivation edges, US and
global. Every edge records what it depends on and how strong the evidence is.

**`lint_lineage.py`** - walks the graph from your target in both directions and
refuses any covariate that is an ancestor or a descendant of it. Predicting a
parent from its own child leaks just as badly as the reverse. It reports every
route it finds, not just the shortest, flags covariates computed from each other
or sharing an ancestor, and fails on any name it does not recognise. Before all
that it validates the manifest itself: cycles, undefined references, missing
fields, duplicate keys, and any `relation`, `confidence` or `measurementBasis`
outside the documented vocabulary. The duplicate-key check matters more than it
sounds. YAML silently keeps the last of a repeated key, so a second
`derivesFrom` would wipe a product's lineage on load and the linter would then
clear a covariate it should have refused.

**`reproduce_svi.py`** - downloads the live CDC SVI file and rebuilds the R2
figures above from scratch.

**`Dockerfile`** and **`requirements.txt`** - a pinned environment, so the
numbers come out the same as mine. The image carries the manifest, the two
scripts and the requirements, nothing else.

## Running it

```bash
pip install pyyaml pandas scikit-learn

python3 lint_lineage.py                 # audit eight real cases
python3 lint_lineage.py --graph         # print the derivation graph
python3 lint_lineage.py --target FEMA_NRI.risk_score \
                        --covariates ACS.EP_POV150 ACS.EP_UNEMP
python3 reproduce_svi.py                # verify the R2 claims from live data
```

On macOS `reproduce_svi.py` usually opens with an SSL certificate error, because
a stock python.org build ships without a certificate bundle. That is expected.
The script falls back to curl on the next line and the figures are unaffected.

If you would rather install nothing:

```bash
docker build -t derives-from .
docker run --rm derives-from                            # the linter
docker run --rm --network none derives-from             # and offline, to prove it
docker run --rm derives-from python reproduce_svi.py    # the R2 figures, needs network
```

The linter needs no API keys, no network, and about a tenth of a second. In
`--target` mode, the one meant for CI, it exits 1 on FAIL, 2 on a broken
manifest or bad usage, and 0 otherwise. An unknown target or covariate name is a
FAIL, not a usage error, so it gets reported next to everything else.

`--target` with no `--covariates` is a usage error. It used to print PASS, which
is a clean bill of health from a check that never ran. If a shell expansion eats
your covariate list, the pipeline has to go red.

Plain `lint_lineage.py` is the built-in demo, not a gate. Its cases are chosen to
fail, so it always exits 0 and prints the tally.

## What it found

```
5 FAIL   1 REVIEW   1 PASS   1 UNTRACED   of 8 audited
```

The clearest failure is FEMA's Risk Score, which reaches the ACS down two routes
at once. This is the linter's own output, unedited:

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

Nobody scanning a list of column names traces both of those reliably. A graph
traversal finds them in milliseconds, which is the whole reason for writing the
graph down. Reporting both routes matters, because they carry different weight:
one goes through a small-area model, the other is arithmetic all the way. An
earlier version of the linter showed only the shortest route, so it picked
whichever had fewest hops regardless of the evidence behind it.

The quiet cases matter as much as the failures. A checker that alarms on
everything is useless, so the suite includes one target with a fully traced
lineage and unrelated covariates, and that comes back `PASS` with no findings.
`UNTRACED` is kept separate: death-certificate mortality has no recorded
ancestors, so there was never anything to find, and calling that a pass would
flatter the tool rather than test it.

---

## Reading the manifest

Every product has a `measurementBasis`:

| value | count | meaning |
|---|---|---|
| `measured` | 39 | direct enumeration, survey, sensor, or registry |
| `modelled` | 9 | output of a statistical or machine learning model |
| `composite` | 12 | deterministic arithmetic over other published products |

This field does a lot of work on its own. No public catalogue currently tells a
census count apart from a random forest prediction, so everyone downstream
treats them as the same kind of number.

Every edge has a `relation`:

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
| `documented` | 41 | stated in the publishing agency's own methodology |
| `inferred` | 4 | strongly implied but not verbatim, treat as provisional |

Confidence is a first-class field on purpose. An unaudited lineage graph would
recreate the exact problem it exists to solve.

One product carries `coPublishedNonInputs`, listing variables that ship in the
same file as the index but take no part in computing it. That field exists
because of the bug above, and its job is to stop anyone re-adding an edge that
has already been removed once.

## What I am not claiming

I am not saying any published result is wrong. Per-target feature lists and fold
structures usually are not available. My claim is about what a benchmark can
tell apart, and it says nothing about anyone's competence or intent.

This is also incomplete: 60 products against an estimated 400 or more official
composite indices worldwide, and four edges are still marked `inferred`. I expect
more of it to be wrong than my own labels suggest, since only the edges I
actually checked are known either way, and the first audit of this file turned up
six errors, four of them in edges I had labelled `certain` or `documented`.

The honest version of this work comes from CDC, FEMA and the Census Bureau
themselves, out of the methodology documents they already publish. They are best
placed to do it and they have nowhere to record it. That last part is what Data
Commons could fix: two new fields on the statistical variable schema,
`derivesFrom` and `measurementBasis`, would give every producer somewhere to put
what they already know.

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

## Citation

Every release is archived on Zenodo. The identifier below always resolves to the
newest version.

> Adeniyi, K. (2026). *derives-from: a derivation manifest for public statistical
> data, with a lineage linter* (Version 1.0.0) [Software].
> Zenodo. https://doi.org/10.5281/zenodo.22274757

```bibtex
@software{adeniyi_derives_from_2026,
  author    = {Adeniyi, Kayode},
  title     = {derives-from: a derivation manifest for public statistical
               data, with a lineage linter},
  year      = {2026},
  version   = {1.0.0},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.22274757},
  url       = {https://github.com/Adeniyikayodee/dependency_manifest}
}
```

## Licence

The manifest and the linter are CC0. The upstream datasets keep their own terms.
