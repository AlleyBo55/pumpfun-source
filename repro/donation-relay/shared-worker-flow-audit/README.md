# Shared donation worker: cleanup flow and mint-source controls

The Relay frontier remains **482/492 normalized windows, 130 raw local body
matches, ten unmatched**. This study does not promote a new candidate.

## What the control flow establishes

The original shared worker (ordinal 112, address 131,136, 10,248 bytes) and the
current reconstructed worker each contain exactly one call to the matched
`DonationContext` drop helper (original ordinal 51), and one call to the matched
transfer helper (ordinal 226). In both functions, every path through the decoded
intra-function graph from entry to an explicit `exit` instruction passes through
the context-drop call. There is also a path from the transfer call's continuation
to that drop call, and no path from that continuation to `exit` which avoids it.

| Relative byte offset | Original worker | Current worker |
| --- | ---: | ---: |
| Transfer helper call | 9,568 | 9,672 |
| Context-drop helper call | 3,152 | 352 |
| Sole explicit exit | 3,160 | 360 |

The cleanup block's location in the linear disassembly is therefore not evidence
that the two programs transfer ownership at different stages. The decoded edges
connect both implementations to their common cleanup block. This finding directs
further work toward source expression, lifetimes and code generation while
preserving the whole-context cleanup path. It does not prove a unique original
Rust source or justify replacing the matched cleanup helper with partial moves.

`report.json` includes every decoded instruction and successor, all direct-call
attributions, and explicit paths supporting the findings. Calls are conservatively
assumed to return. Conditional edges are both included; branch satisfiability,
nonreturning callees, indirect targets, error meanings, memory safety and runtime
success are not proved by this graph. A transfer-to-cleanup path is not proof of
a successful transfer. No whole-body or whole-file identity is claimed.

## Five compiled source controls

Reading the original instructions suggested testing a separate key copied from
the cloned mint account and eager loading of the whitelist slice. These are
hypotheses, not recovered source facts.

| Source form | Worker bytes | Complete normalized match |
| --- | ---: | --- |
| Shadow the outer mint key with the cloned account's key | 10,480 | No |
| Mint-check helper accepting a whitelist slice, normal inlining | 10,576 | No |
| Same helper with `inline(always)` | 10,576 | No |
| Local whitelist slice, existing outer key | 10,392 | No |
| Local whitelist slice and shadowed key | 10,424 | No |

All five retain the 482-window frontier without gaining or losing a matched
window. Their full source input maps, root compiler invocations, source snapshots,
and stripped/unstripped binaries are retained. The helper variants produce the
same worker hash. No candidate is accepted from approximate similarity or size.
These are native-compiler/Linux-library builds; no fresh Linux-compiler or runtime
replay is claimed for rejected variants. The preceding accepted checkpoint keeps
its own independent replay evidence.

## Verification

```sh
python3 -B repro/donation-relay/shared-worker-flow-audit/test_flow.py
python3 -B repro/donation-relay/shared-worker-flow-audit/verify.py
python3 -I -B repro/donation-relay/shared-worker-flow-audit/verify.py
python3 -B repro/donation-relay/shared-worker-flow-audit/verify.py \
  --materialize /tmp/relay-mint-scope --variant mint-scope-shadow
```

The standard-library verifier binds the existing 56-input burn/close checkpoint,
reconstructs each source map, reanalyzes the entire function inventory, and
recomputes the graphs from original and current binary bytes. The eight focused
graph tests check bypass paths, unconditional branches, LDDW continuation slots,
invalid targets, returning calls, cycles JMP32 edges and unsupported control opcodes. Verification does not
recompile or execute the target programs. The retained controllers describe the
build recipe; adjust workspace paths before rerunning them.
