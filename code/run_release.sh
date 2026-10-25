#!/bin/bash
# One command from a Gaia SSO release to a validated rotation-period catalogue.
#   RELEASE_PREFIX  bulk-file prefix on the Gaia CDN (DR3: Gaia/gdr3/Solar_system/sso_observation/)
#   WORKERS         processes (default 10)       SKIP_FETCH=1 / SKIP_PREP=1 to reuse existing files
# Everything is fitted on TUNE or chosen by the null-test rule; TEST is only reported.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3}; WORKERS=${WORKERS:-10}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PIPELINE_PAB=1
log() { echo "$(date '+%F %T') $*" | tee -a release.log; }

if [ -z "${SKIP_FETCH:-}" ]; then log "1/8 fetch ${RELEASE_PREFIX:?}"; $PY fetch_bulk.py "$RELEASE_PREFIX" data/gaia_sso; fi
if [ -z "${SKIP_PREP:-}" ];  then log "2/8 transits"; $PY prep_gaia.py; fi
log "3/8 period search (all asteroids with >= 25 transits)"; $PY pipeline.py --workers "$WORKERS"
log "4/8 null tests on 4000 random asteroids without an LCDB period"
$PY - <<'PYEOF'
import random, calibrate2 as c
lc = c.load_lcdb(); res = c.load_results()
u = sorted(r["num"] for r in res if r["num"] not in lc); random.seed(3)
open("null_nums.txt", "w").write("\n".join(map(str, random.sample(u, min(4000, len(u))))))
PYEOF
PIPELINE_NULL=1 PIPELINE_RESULTS=results_null $PY pipeline.py --workers "$WORKERS" --only-file null_nums.txt
PIPELINE_NULL=1 PIPELINE_NULL_BLOCK=1.0 PIPELINE_RESULTS=results_null_block $PY pipeline.py --workers "$WORKERS" --only-file null_nums.txt
log "5/8 tier-A threshold from the null-test rule"; $PY choose_threshold.py
export CONF_PROB_MIN=$($PY -c "import json; print(json.load(open('threshold.json'))['threshold'])")
log "6/8 calibration (TUNE) and catalogue, threshold $CONF_PROB_MIN"; $PY calibrate2.py > /dev/null
log "7/8 literature and new candidates"; $PY compare_lit.py > /dev/null; $PY make_new.py
log "8/8 statistics and figures"; $PY stats_final.py > /dev/null; $PY make_figures.py
log "done: catalog.csv, new_candidates.csv, stats_final.json, figures/ (novelty beyond the six catalogues: run novelty scripts)"
