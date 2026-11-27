"""Check the new paired constraints and the finite oracle coupling independently."""
from pathlib import Path
from itertools import combinations
import ast
import json
import math
import numpy as np
from scipy.optimize import linprog
from scipy.stats import beta, binom

parsed = ast.parse(Path('tmp/verify_engineering_reformulation.py').read_text(encoding='utf-8'))
helpers = ast.Module(body=[node for node in parsed.body if isinstance(node, ast.FunctionDef)
                          and node.name in {'discrepancy', 'endpoints'}], type_ignores=[])
scope = {'np': np}
exec(compile(helpers, '<DW inversion>', 'exec'), scope)
endpoints = scope['endpoints']
rng = np.random.default_rng(596202611242)
solves = paired_cases = 0
empty_intersections = theta_zero_cases = 0
max_combination_error = 0.

def exact_binomial_interval(count, size, error):
    lower = beta.ppf(error / 2, count, size - count + 1) if count else 0.
    upper = beta.ppf(1 - error / 2, count + 1, size - count) if count < size else 1.
    return lower, upper

def lp(cost, aub, bub, aeq, beq):
    global solves
    solves += 1
    return linprog(cost, A_ub=aub, b_ub=bub, A_eq=aeq, b_eq=beq,
                   bounds=(0, None), method='highs')

for trial in range(30):
    size = [4, 6, 10][trial % 3]
    theta = [0., 1., 3.][(trial // 3) % 3]
    theta_zero_cases += theta == 0
    # Exact finite input laws, including threshold equalities and repeated responses.
    response = np.array([0., 0., 1., 2., 3.])
    residual_true = rng.choice([-2., -1., 0., 1.], size=len(response))
    weights = rng.dirichlet(np.ones(len(response)))
    if trial % 5 == 0:
        residual_true = np.ones(len(response))
    elif trial % 5 == 1:
        residual_true = -response - 1
    observed_inputs = rng.choice(len(response), size=size, p=weights)
    residual_sample = residual_true[observed_inputs]
    observed = np.unique(residual_sample)
    counts = np.searchsorted(np.sort(residual_sample), observed, side='right')
    table = np.column_stack(endpoints(size, theta))
    if theta == 0 and size % 2 == 0:
        table[size // 2] = .5
    lower_rank = table[counts, 0]
    upper_rank = table[np.r_[0, counts[:-1]], 1]
    thresholds = -response
    breaks = np.unique(np.r_[thresholds, observed])
    residual_grid = np.unique(np.r_[breaks[0] - 1, breaks,
                                   (breaks[:-1] + breaks[1:]) / 2, breaks[-1] + 1])
    failure = (residual_grid[None, :] <= thresholds[:, None]).astype(float).ravel()
    opened = (residual_grid[None, :] < observed[:, None]).astype(float)
    closed = (residual_grid[None, :] <= observed[:, None]).astype(float)
    aub = np.r_[np.tile(opened, (1, len(response))), -np.tile(closed, (1, len(response)))]
    bub = np.r_[upper_rank, -lower_rank]
    aeq = np.kron(np.eye(len(response)), np.ones((1, len(residual_grid))))
    original_low = lp(failure, aub, bub, aeq, weights)
    original_high = lp(-failure, aub, bub, aeq, weights)
    assert original_low.success and original_high.success
    original_interval = original_low.fun, -original_high.fun
    count = np.count_nonzero(response[observed_inputs] + residual_sample <= 0)
    bin_interval = exact_binomial_interval(count, size, .08)
    # Include conflicting paired bounds to test infeasibility rather than inverted intervals.
    candidates = [bin_interval]
    if original_interval[0] > .01:
        candidates.append((0., original_interval[0] / 2))
    elif original_interval[1] < .99:
        candidates.append(((1 + original_interval[1]) / 2, 1.))
    for bin_lower, bin_upper in candidates:
        paired_cases += 1
        expected = max(original_interval[0], bin_lower), min(original_interval[1], bin_upper)
        new_aub = np.r_[aub, failure[None, :], -failure[None, :]]
        new_bub = np.r_[bub, bin_upper, -bin_lower]
        combined_low = lp(failure, new_aub, new_bub, aeq, weights)
        combined_high = lp(-failure, new_aub, new_bub, aeq, weights)
        if expected[0] > expected[1] + 1e-8:
            empty_intersections += 1
            assert combined_low.status == 2 and combined_high.status == 2
        else:
            assert combined_low.success and combined_high.success
            err = max(abs(combined_low.fun - expected[0]), abs(-combined_high.fun - expected[1]))
            max_combination_error = max(max_combination_error, err)
            assert err < 1e-8

# Exact binomial coverage over every possible count, including zero and full counts.
binomial_cases = 0
minimum_coverage = 1.
for size in [1, 2, 5, 10, 30]:
    intervals = np.array([exact_binomial_interval(count, size, .08) for count in range(size + 1)])
    for probability in np.r_[0., np.linspace(.0001, .9999, 201), 1.]:
        covered = (intervals[:, 0] <= probability) & (probability <= intervals[:, 1])
        coverage = np.sum(binom.pmf(np.arange(size + 1), size, probability) * covered)
        assert coverage >= .92 - 1e-12
        minimum_coverage = min(minimum_coverage, float(coverage))
        binomial_cases += 1

# Exhaustively verify the adaptive no-hit transcript coupling, with repeated queries allowed.
oracle_regions = oracle_paths = 0
for cells in [8, 11, 15]:
    budget = 3
    null_outputs = np.array([0., .05, .2, .6])
    def execute(region, seed):
        query = seed % cells
        trace = []
        hits = 0
        for step in range(budget):
            hit = query in region
            trace.append((query, hit))
            hits += hit
            if seed == 0 and not hit:
                query = query
            else:
                query = (query + 1 + step + seed + 3 * hit) % cells
        return trace, (1. if hits else null_outputs[seed])
    null = [execute(set(), seed) for seed in range(4)]
    for number_failed in [1, 2, 3]:
        probability = number_failed / cells
        no_hit_bound = math.comb(cells - budget, number_failed) / math.comb(cells, number_failed)
        errors = []
        for subset in combinations(range(cells), number_failed):
            region = set(subset)
            outcomes = []
            for seed in range(4):
                trace, output = execute(region, seed)
                null_trace, null_output = null[seed]
                if not any(query in region for query, _ in null_trace):
                    assert trace == null_trace and output == null_output
                outcomes.append(output < probability)
                oracle_paths += 1
            errors.append(np.mean(outcomes))
            oracle_regions += 1
        baseline_small = np.mean(null_outputs < probability)
        assert np.mean(errors) + 1e-14 >= baseline_small * no_hit_bound

report = {
    'paired_intersection_cases': paired_cases,
    'linear_programs_solved': solves,
    'empty_intersections_correctly_infeasible': empty_intersections,
    'theta_zero_base_cases': theta_zero_cases,
    'maximum_combined_interval_lp_difference': max_combination_error,
    'exact_binomial_coverage_checks': binomial_cases,
    'minimum_binomial_coverage_for_nominal_0_92': minimum_coverage,
    'exhaustive_hidden_regions': oracle_regions,
    'adaptive_query_paths_checked': oracle_paths,
    'passed': True,
}
Path('tmp/information_limits_verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
