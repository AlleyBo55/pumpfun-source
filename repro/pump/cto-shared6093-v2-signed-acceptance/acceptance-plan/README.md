# V2 acceptance plan — preparation only

Two independent lanes: ordinary363 preservation and six-case/twelve-side shared6093 finite acceptance. They use distinct durable one-attempt outputs. Run neither until both plan reviews, emitted review and root admission are complete. No runtime has been executed by this preparation.

Each lane has an independently sealed manifest and mandatory supplemental `gate.py`. Launch requires the lane seal plus separately pinned emitted-review seal and root-admission hash. Root admission must bind each lane seal in `plan_seals`; exact schema is described by each lane README and enforced in admission.py. Lower-level controllers are retained method artifacts, not authorized direct entry points. Read-only gate preflights need only `--expected-seal`; `--execute` additionally requires both admission pins. Never retry an existing claimed lane.

No historical compiler identity, exact original output identity, universal shared field map or full ABI closure is claimed. Original exit2/cache-review receipt and null inner compiler/strip statuses remain unchanged. Old58b/113b controls, prior6e signed results and held v1 evidence remain historical; current candidate fdf/source950d is explicit.
