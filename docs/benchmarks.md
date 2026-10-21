# Benchmark methodology

Run `python benchmarks/run_benchmark.py` against a running API configured with a real backend. The script reports request latency and response size only; it does not measure naturalness or pronunciation.

For credible comparisons, use identical fixed text, multiple repetitions, a documented hardware/model configuration, warm-up runs, median and percentile latency, real-time factor where applicable, error rate, and human listening evaluation. Do not compare cherry-picked samples or claim superiority from a single run.
