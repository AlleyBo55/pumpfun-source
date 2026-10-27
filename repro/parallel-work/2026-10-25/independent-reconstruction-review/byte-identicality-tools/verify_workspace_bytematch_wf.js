export const meta = {
  name: 'verify-workspace-bytematch',
  description: 'Independently re-derive the key claims about converting pumpfun to a single workspace vs remap, for byte-identicality',
  phases: [
    { title: 'Rederive', detail: 'one agent per program independently re-measures from the ELFs' },
    { title: 'Audit', detail: 'adversarial audit of the conclusion' },
  ],
}

// args: { scratch, programs: [{prog, dir, orig, before, after, remap}] }
const A = args

const SCHEMA = {
  type: 'object',
  properties: {
    program: { type: 'string' },
    // reordering claim: before vs after same instruction multiset but reordered
    text_size_before: { type: 'integer' },
    text_size_after: { type: 'integer' },
    text_identical_before_after: { type: 'boolean' },
    masked_opcode_multiset_overlap_pct: { type: 'number' },
    // remap claim: remap .text identical to standalone-before (no reorder)
    text_identical_before_remap: { type: 'boolean' },
    // path strings
    orig_path_strings: { type: 'integer' },
    before_path_strings: { type: 'integer' },
    after_path_strings: { type: 'integer' },
    remap_path_strings: { type: 'integer' },
    conclusion: { type: 'string' },
  },
  required: ['program', 'text_identical_before_after', 'masked_opcode_multiset_overlap_pct',
    'text_identical_before_remap', 'before_path_strings', 'after_path_strings', 'remap_path_strings', 'conclusion'],
}

const AUDIT = {
  type: 'object',
  properties: {
    reordering_claim_holds: { type: 'boolean' },
    remap_is_clean_path_only: { type: 'boolean' },
    workspace_is_not_a_clean_win: { type: 'boolean' },
    discrepancies: { type: 'array', items: { type: 'string' } },
    verdict: { type: 'string' },
  },
  required: ['reordering_claim_holds', 'remap_is_clean_path_only', 'workspace_is_not_a_clean_win', 'verdict'],
}

phase('Rederive')
const measured = await parallel(A.programs.map(p => () => agent(
  `Independently verify byte-identicality claims for Solana program "${p.prog}". Write your OWN python3 (parse ELF section headers via struct; .text is the section named ".text"). Do NOT use any script under ${p.scratch || A.scratch}.

Files:
  ORIGINAL: ${p.orig}
  BEFORE (committed source, built STANDALONE, bare src/ paths): ${p.before}
  AFTER  (same source, built as single-member WORKSPACE, programs/${p.dir}/src/ paths): ${p.after}
  REMAP  (same source, built STANDALONE + --remap-path-prefix, programs/${p.dir}/src/ paths): ${p.remap}

Determine and report:
1. .text section size in BEFORE and AFTER. Are the .text bytes identical between BEFORE and AFTER?
2. Treat .text as 8-byte instruction slots. Mask bytes 2..7 of each slot (keep opcode+regs). Is the MULTISET (order-independent Counter) of masked slots identical between BEFORE and AFTER? Report overlap %. (If ~100%, the two binaries contain the same instructions reordered.)
3. Is the .text of REMAP byte-identical to the .text of BEFORE? (If yes, --remap-path-prefix recovers paths WITHOUT reordering.)
4. Count exact original source-path strings 'programs/${p.dir}/src/<...>.rs' present in ORIGINAL, and how many of the ORIGINAL's set appear in BEFORE, AFTER, REMAP. Use: strings <so> | grep -oE 'programs/${p.dir}/src/[A-Za-z0-9_/]+\\.rs' | sort -u.
Be adversarial: if AFTER differs from BEFORE by more than reordering+path-strings, say so.`,
  { label: `verify:${p.prog}`, phase: 'Rederive', schema: SCHEMA }
)))

phase('Audit')
const audit = await agent(
  `Adversarially audit this conclusion about converting the pumpfun repo to a single Cargo workspace (goal: make candidate binaries byte-match the deployed originals):

CONCLUSION:
(a) Building a program as a workspace member (vs standalone) recovers the 'programs/<dir>/src/' path strings but REORDERS functions in .text (same instruction multiset, different layout) — it is NOT a clean path-only change. Mechanism: the crate build context/metadata changes the symbol layout.
(b) --remap-path-prefix recovers the SAME path strings while keeping .text byte-identical to the standalone build (no reorder) and no dependency change — a clean path-only gain.
(c) A single MULTI-member workspace additionally forces dependency-version unification (spl-token-2022 6.0.0 -> 7.0.0, solana-program 2.2.1/2.3.0) that changes code bytes — strictly worse. (Evidence: shared-lock resolve picked spl-token-2022 7.0.0 which was not cached, so the offline build failed.)
(d) Path-string recovery for the committed (flat) candidates is small (pump 9, pump_amm 4, mayhem 3 of 33/33/9 files) and whole-binary byte-match stays ~36-42%, dominated by function ordering (which matches neither standalone nor the original) plus source-bound codegen.

Independent per-program measurements: ${JSON.stringify(measured)}

Decide: does the reordering claim (a) hold? Is remap (b) genuinely clean (text_identical_before_remap true for all)? Is the workspace conversion therefore NOT a clean win? Flag any measurement that contradicts the conclusion. Give a crisp verdict and the single recommended action.`,
  { label: 'audit', phase: 'Audit', schema: AUDIT }
)

return { measured, audit }
