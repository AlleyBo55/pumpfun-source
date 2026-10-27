# Fees wrapper code-generation controls

Changing only the root crate's code-generation-unit count does **not** recover
`__private::__global::initialize_buyback` (original 650,064, 1,208 bytes).
The current one-unit wrapper has 1,200 bytes. After the existing call/pointer
masks, its only differences are one missing halfword store and the corresponding
one-instruction branch displacement. The original stores `0xffff` at `fp-562`.

The generated Rust already defaults the two bump fields to `u8::MAX`. The
multi-unit builds retain a default store, but at another stack offset and with
other wrapper differences. This excludes these unit-count substitutions as a
complete recovery; it does not prove which original source/compiler input
caused the store to survive optimization.

| Root codegen units | Unique pairs | Ambiguous original windows | Unmatched | New / lost covered windows | Wrapper bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 (fresh control) | 380 | 147 | 58 | 0 / 0 | 1,200 |
| 2 | 262 | 138 | 185 | 0 / 127 | 2,168 |
| 4 | 241 | 153 | 191 | 0 / 133 | 1,272 |
| 8 | 233 | 131 | 221 | 0 / 163 | 1,680 |
| 16 | 235 | 129 | 221 | 0 / 163 | 2,264 |

All 36 source/dependency-manifest inputs match the
[buyback-origin parent](../fees-buyback-context-origin/README.md). The override
is passed after `cargo rustc --` and affects only the root crate. The one-unit
control reproduces both parent artifacts exactly. All five pinned Linux v1.44
builds, their commands/logs, stripped and symbol-bearing outputs, and complete
coverage deltas are retained. No rejected build is promoted or executed in the
VM, and this static study adds no behavioral coverage.

Run `python3 -B research/fees-wrapper-codegen-controls/verify.py` to verify the
input/build/artifact bindings and recompute all comparisons. The parent
380-pair / 58-unmatched research frontier is unchanged by this study.
