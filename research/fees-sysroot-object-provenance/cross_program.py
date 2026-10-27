"""Raw helper-body occurrences and direct-call boundary evidence in three captures."""
import struct

import verify as v


def dynamic_relocations(elf):
    rows = []
    for section in elf.sections:
        if section["type"] == 4:
            v.require(False, "RELA is outside this capture reader's scope")
        if section["type"] != 9:
            continue
        v.require(section["entsize"] == 16 and section["size"] % 16 == 0, "bad REL table")
        for at in range(section["offset"], section["offset"] + section["size"], 16):
            address, info = struct.unpack_from("<QQ", elf.data, at)
            rows.append(dict(virtual_address=address, type=info & 0xffffffff, symbol_index=info >> 32))
    return rows


def direct_call_entries(elf):
    """Decode generic SBF relative calls; exclude R_BPF_64_32 external relocations.

    This is a direct-call boundary ledger, not exhaustive function discovery.
    All addresses are converted through the .text section, not assumed to equal
    file offsets. LDDW continuation words are never decoded as instructions.
    """
    v.require((elf.kind, elf.machine, elf.flags) == (3, 263, 0), "expected generic SBF executable")
    _, text = elf.section_named(".text")
    low, high = text["offset"], text["offset"] + text["size"]
    v.require(text["size"] % 8 == 0, "unaligned text size")
    external_calls = {row["virtual_address"] for row in dynamic_relocations(elf) if row["type"] == 10}
    entries = {}
    at = low
    while at < high:
        insn = v.checked_slice(elf.data, at, 8)
        if insn[0] == 0x18:  # LDDW is a two-slot instruction.
            v.require(at + 16 <= high, "truncated LDDW")
            at += 16
            continue
        address = text["addr"] + at - low
        if insn[:2] == b"\x85\x10" and address not in external_calls:
            displacement = struct.unpack_from("<i", insn, 4)[0]
            target_address = address + 8 + displacement * 8
            relative = target_address - text["addr"]
            if 0 <= relative < text["size"] and relative % 8 == 0:
                target = low + relative
                entries.setdefault(target, []).append(dict(
                    file_offset=at, virtual_address=address, instruction_hex=insn.hex(),
                    signed_displacement=displacement, target_virtual_address=target_address,
                    target_file_offset=target))
        at += 8
    return entries


def raw_occurrences(elf, needle):
    _, text = elf.section_named(".text")
    end = text["offset"] + text["size"]
    at = text["offset"]
    found = []
    while (at := elf.data.find(needle, at, end)) >= 0:
        found.append(at)
        at += 1
    return found


def analyze(package=v.HERE, repo=v.REPO):
    provenance = v.read_json(package / "provenance.json")
    for name, identity in provenance["external_inputs"].items():
        data = v.local_path(repo, name).read_bytes()
        v.require(len(data) == identity["bytes"] and v.digest(data) == identity["sha256"],
                  "changed external input: " + name)
    selected = v.read_json(repo / provenance["selected_helpers"])
    folder = v.local_path(repo, provenance["builds"]["v144-build-01"])
    symbols = v.Elf((folder / "unstripped.so").read_bytes())
    stripped = v.Elf((folder / "pump_fees_candidate.so").read_bytes())
    helpers, identities = {}, {}
    for key in ("core_fmt_write", "integer_entry"):
        record = selected["v144-build-01"]["helpers"][key]
        symbol, = record["names"]
        function = symbols.function(symbol)
        code = v.body(symbols, function)
        v.require((function["offset"], len(code), v.digest(code)) ==
                  (record["candidate_start"], record["bytes"], record["raw_sha256"]),
                  "v144 helper record differs")
        v.require(v.checked_slice(stripped.data, function["offset"], len(code)) == code,
                  "v144 stripped helper differs")
        name = "v144_" + key
        helpers[name] = code
        identities[name] = dict(symbol=symbol, bytes=len(code), sha256=v.digest(code),
                                source="retained v1.44 linked Fees build")
    obj = v.Elf((package / "core.rcgu.o").read_bytes())
    function = obj.function(provenance["symbol"])
    code = v.body(obj, function)
    helpers["v1461_fmt_write"] = code
    identities["v1461_fmt_write"] = dict(symbol=provenance["symbol"], bytes=len(code),
        sha256=v.digest(code), source="retained object from official v1.46.1 generic SBPF libcore")
    captures = {}
    for program, path in provenance["cross_program_captures"].items():
        elf = v.Elf(v.local_path(repo, path).read_bytes())
        _, text = elf.section_named(".text")
        entries = direct_call_entries(elf)
        relocations = dynamic_relocations(elf)
        ordered = sorted(entries)
        results = {}
        for name, code in helpers.items():
            matches = []
            for start in raw_occurrences(elf, code):
                end = start + len(code)
                following = next((at for at in ordered if at > start), None)
                address = text["addr"] + start - text["offset"]
                matches.append(dict(start=start, end=end,
                    instruction_aligned=(start - text["offset"]) % 8 == 0,
                    start_direct_callers=entries.get(start, []),
                    end_direct_callers=entries.get(end, []),
                    next_direct_call_target=following,
                    loader_relocations=[row for row in relocations if address <= row["virtual_address"] < address + len(code)],
                    occupies_complete_direct_call_window=bool(entries.get(start)) and following == end,
                    raw_sha256=v.digest(elf.data[start:end])))
            results[name] = matches
        captures[program] = dict(path=path, bytes=len(elf.data), sha256=v.digest(elf.data),
            text_file_offset=text["offset"], text_virtual_address=text["addr"],
            text_bytes=text["size"], text_sha256=v.digest(elf.section_bytes(elf.section_named(".text")[0])),
            helper_occurrences=results)
    return dict(helpers=identities, captures=captures, comparison="unmodified raw bytes",
                boundary_scope="direct-call targets only; not exhaustive debug-symbol function recovery",
                normalized_comparisons=0, compiler_executions=0, unique_historical_compiler_proved=False)
