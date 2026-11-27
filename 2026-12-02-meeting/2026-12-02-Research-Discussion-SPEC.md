# Research Discussion Specification

## Research scope

Study power- and carbon-aware LLM serving on heterogeneous GPU systems at single-server and single-rack scales. Main objective: energy efficiency under latency SLOs and power constraints. Report power, energy, operational carbon, embodied carbon, and serving performance.

## Candidate order

1. **A — Workload-aware energy optimization of multi-tier KV cache.** The leading candidate because it connects established tiered KV behavior with the selected energy objective. Validate storage timing, I/O energy, shared batch accounting, calibration feasibility, and SLO effects first.
2. **B — Energy-efficient workload scheduling on heterogeneous GPU racks.** Alternative; energy-aware scheduling exists in DynamoLLM/FREESH, so check overlap, locality and batch-energy treatment before claiming a gap.
3. **C — Energy-aware KV-cache management for agentic serving.** Specialized workload candidate; session-aware retention is known and public trace/timing availability is unresolved. Could be a workload under A.

## Gap validation

Characterize chat/RAG/agentic traces; validate simulation against available power/performance measurements; compare feasible tier configurations and recompute/restore policies at identical completed work, hardware, policy, and SLO. First ask whether model fidelity changes feasible configuration rankings. Do not assume it will.

## Simulator plan

Audit and reproduce a pinned LLMServingSim 2.0 version. Preserve current capabilities where verified. Calibrate proposed phase/batch, storage-I/O, communication, operational-carbon, and embodied-carbon extensions only where necessary. An idle-power parameter alone is not evidence of SSD cache timing or contention support.

## Accounting safeguards

- Integrate power over a stated horizon to obtain energy.
- Do not add isolated per-request estimates on top of shared batch energy.
- Avoid double counting GPU board, HBM, and baseline power.
- Apply PUE once; use compatible energy and carbon-intensity units.
- Treat embodied carbon as lifecycle allocation; runtime eviction does not erase manufacturing emissions.
- Keep workload completion, quality, hardware, and SLO comparable.

## Unresolved checks

- Pin simulator revision and reproduce published example.
- Verify SSD KV timing, movement, queueing, and contention support.
- Verify power-model calibration coverage for target GPUs, DRAM, SSD, and links.
- Identify accessible hardware meters, request traces, and agent tool timing.
- Reconcile GreenCache power assumptions and agentic session-residency literature before fixing the final research question.
