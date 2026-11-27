"""Check full residual envelopes on every breakpoint and intervening interval."""
from pathlib import Path
import json
import numpy as np

rng = np.random.default_rng(59620261125)
cases = equalities = 0
maximum_error = 0.0
for K in range(1, 9):
    for replicate in range(4):
        observed = np.sort(rng.choice(np.arange(-40, 41), size=K, replace=False)).astype(float)
        columns = np.arange(1, 2 * K + 2)
        rows = np.arange(K + 1)
        ranks = np.arange(1, K + 1)
        h_upper = (columns[None, :] <= 2 * rows[:, None] + 1).astype(float)
        h_lower = (columns[None, :] <= 2 * rows[:, None]).astype(float)
        open_cells = (columns[:, None] < 2 * ranks).astype(float)
        closed_cells = (columns[:, None] <= 2 * ranks).astype(float)
        multipliers = [(np.zeros(K), np.zeros(K)), (np.ones(K), np.ones(K))]
        for k in range(K):
            unit = np.eye(K)[k]
            multipliers.extend([(unit, np.zeros(K)), (np.zeros(K), unit)])
            assert np.all((rows >= k + 1)[:, None] + open_cells[:, k][None, :] >= h_upper)
            assert np.all((rows >= k + 1)[:, None] - 1 + closed_cells[:, k][None, :] <= h_lower)
        for _ in range(6):
            lam, gamma = rng.uniform(0, 3, (2, K))
            gamma[rng.random(K) < .4] = 0
            multipliers.append((lam, gamma))
        thresholds = np.r_[observed[0] - 1, observed,
                           (observed[:-1] + observed[1:]) / 2,
                           observed[-1] + 1]
        for lam, gamma in multipliers:
            cell_penalty = open_cells @ lam - closed_cells @ gamma
            finite_upper = np.max(h_upper - cell_penalty[None, :], axis=1)
            finite_lower = np.min(h_lower + cell_penalty[None, :], axis=1)
            assert np.allclose(cell_penalty[1::2], cell_penalty[2::2] - gamma)
            for threshold in thresholds:
                row = int(np.searchsorted(observed, threshold, side='right'))
                # The full pointwise objectives are constant between these breakpoints.
                # Checking the points themselves retains every open/closed distinction.
                breaks = np.unique(np.r_[observed, threshold])
                candidates = np.r_[breaks[0] - 1, breaks,
                                   (breaks[:-1] + breaks[1:]) / 2, breaks[-1] + 1]
                penalty = ((candidates[:, None] < observed) @ lam
                           - (candidates[:, None] <= observed) @ gamma)
                indicator = (candidates <= threshold).astype(float)
                actual_upper = np.max(indicator - penalty)
                actual_lower = np.min(indicator + penalty)
                error = max(abs(actual_upper - finite_upper[row]),
                            abs(actual_lower - finite_lower[row]))
                assert error < 1e-10, (K, threshold, lam, gamma, error)
                maximum_error = max(maximum_error, float(error))
                cases += 1
                equalities += int(np.any(threshold == observed))

report = {'fixed_multiplier_envelope_cases': cases,
          'threshold_equality_cases': equalities,
          'largest_number_of_distinct_residuals': 8,
          'maximum_envelope_difference': maximum_error,
          'nonnegative_multipliers_with_zero_components_included': True,
          'all_single_rank_certificates_checked': True}
Path('tmp/partition_duality_envelope_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
