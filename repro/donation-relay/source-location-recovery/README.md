# Relay: recover the audited source-location values

The combined source build resolves **all 43 path/line/column differences** found
by the [independent location audit](../../../research/relay-location-data-audit/README.md).
All **346 recognized location pairs** in the same audited cohort now agree, while
**480/492 normalized instruction windows** remain matched and **12 unmatched**.
Both combined builds have **130 raw local body matches**, and each passes fresh
replay of all **536 records / 534 unique fixtures**. Whole-file identity remains false.

This is additional data recovery, not nine more functions or complete data
closure. The audit covers location-shaped records in uniquely matched windows;
ambiguous matches, unmatched functions and other data objects remain outside its
scope. Absolute pointer/relocation equality is also not established by equal
file/line/column values.

## Independent source-build controls

| Build | Recognized pairs | Unequal location values | Normalized windows | Raw local matches |
| --- | ---: | ---: | ---: | ---: |
| Pinned mint-pair parent | 346 | 43 | 480 | 127 |
| Program macro column | 346 | 10 | 480 | 127 |
| Event source files | 346 | 35 | 480 | 149 |
| Mint borrow source file | 346 | 42 | 480 | 130 |
| Remainder push coordinate | 346 | 42 | 480 | 127 |
| **Combined, Darwin compiler / Linux libraries** | **346** | **0** | **480** | **130** |
| **Combined, fully Linux build** | **346** | **0** | **480** | **130** |

The four individual controls and first combined build begin with the same pinned
52-input source and apply their named proposals. Both combined builds use the
same 56 source inputs. All changes are
ordinary Rust source placement, whitespace or `include!` structure:

- Move `#[program]` to column 1 while keeping line 36.
- Place three unchanged event declarations at line 5, column 1 in their captured
  `events/v1/` source paths, included in their original namespace.
- Put the unchanged mint helper in `tools/checks.rs`, with the borrow token at
  line 96, column 31.
- Put the existing remainder-vector push at line 46, column 20, retaining the
  previously recovered indexed-update coordinate.

The program-column control changes exactly one byte of the full stripped ELF:
offset 773492 changes from 5 to 1. The other controls also change layout; their
raw-match counts must not be treated as a ranking of source or semantic recovery.
For example, the event-only build has more raw local coincidences but leaves 35
recognized location differences, whereas the combined build resolves all 43.

No original executable bytes enter the Rust compiler. No generated executable
is patched. These source layouts reproduce measured coordinates, not the
unknown historical comments, whitespace or exact source organization.

## Verification and scope

```sh
python3 -B repro/donation-relay/source-location-recovery/verify.py
python3 -B repro/donation-relay/source-location-recovery/verify.py \
  --materialize /tmp/relay-location-source --variant combined
```

The verifier checks all parent and package hashes, reconstructs exact source
inputs, re-analyzes complete instruction windows, and requires the same 346
`(original-window, reference-offset)` pairs before and after every change. It
reads each 24-byte object using the parent's bounded pointer/length/line/column
rules. Thus a record becoming unrecognized or a function leaving the matched
cohort cannot silently reduce the difference count. No prior normalized match
is lost in any of the six builds.

`location-values.json` contains the original and candidate object bytes, pointer
relocations, bounded source strings, and decoded values for every paired use.
Both combined candidates receive fresh runtime replay in this study. Their
signatures, fixture bindings, original observations and effects are rechecked
with the unchanged runner and comparator; allocation-failure and privileged
settlement paths are not claimed as newly executed coverage.

The four independent source-change controls and the first combined build use
the parent's Darwin v1.48 compiler/linker with official Linux v1.48 target
libraries. `combined-linux` independently compiles the same 56 inputs with the
actual Linux SDK in the existing isolated Ubuntu environment, then replays its
new binary. It does not borrow acceptance from the pre-coordinate checkpoint.
Selected sources and artifacts remain unchanged. Complete sections, relocations,
indirect calls, semantic equivalence and the remaining 12 bodies still need work.
