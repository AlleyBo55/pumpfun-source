#!/usr/bin/env python3
"""Check raw sysroot/object/link relationships without executing release tools."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct
import tarfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes())


def checked_slice(data, start, size):
    require(start >= 0 and size >= 0 and start + size <= len(data), "range outside input")
    return data[start:start + size]


def local_path(root, name):
    path = PurePosixPath(name)
    require(not path.is_absolute() and bool(path.parts) and
            all(p not in ("..", ".") for p in path.parts) and
            "\\" not in name and ":" not in name and path.as_posix() == name,
            "noncanonical relative path")
    return root.joinpath(*path.parts)


def ar_members(data):
    """Yield exact member payloads; support GNU long names and BSD extended names."""
    require(data[:8] == b"!<arch>\n", "not a regular ar archive")
    pos, names = 8, b""
    seen = set()
    while pos < len(data):
        header = checked_slice(data, pos, 60)
        require(header[58:] == b"`\n", "bad ar header trailer")
        size = int(header[48:58])
        start = pos + 60
        raw = checked_slice(data, start, size)
        name = header[:16].decode("ascii").rstrip()
        if name == "//":
            names = raw
        elif name.startswith("#1/"):
            length = int(name[3:])
            name = checked_slice(raw, 0, length).rstrip(b"\0").decode()
            start += length
            raw = raw[length:]
        elif name.startswith("/") and name[1:].isdigit():
            offset = int(name[1:])
            require(offset < len(names), "ar long-name offset outside table")
            end = names.find(b"/\n", offset)
            require(end >= 0, "unterminated ar long name")
            name = names[offset:end].decode()
        elif name not in ("/", "/SYM64/"):
            name = name.removesuffix("/")
        require(name not in seen, "duplicate ar member: " + name)
        seen.add(name)
        yield name, start, raw
        pos += 60 + size
        if size % 2:
            require(checked_slice(data, pos, 1) == b"\n", "bad ar padding")
            pos += 1


class Elf:
    """Small ELF64-LE reader for section-backed symbols, with bounded reads."""
    def __init__(self, data):
        self.data = data
        require(data[:7] == b"\x7fELF\x02\x01\x01", "expected ELF64 little endian")
        checked_slice(data, 0, 64)
        self.kind, self.machine = struct.unpack_from("<HH", data, 16)
        require(self.kind in (1, 2, 3), "unsupported ELF type")
        self.flags = struct.unpack_from("<I", data, 48)[0]
        table = struct.unpack_from("<Q", data, 40)[0]
        stride, count, strings_index = struct.unpack_from("<HHH", data, 58)
        require(stride == 64 and 0 < strings_index < count, "unsupported section table")
        checked_slice(data, table, count * stride)
        self.sections = []
        for index in range(count):
            row = struct.unpack_from("<IIQQQQIIQQ", data, table + index * stride)
            section = dict(zip(("name_offset", "type", "flags", "addr", "offset",
                                "size", "link", "info", "alignment", "entsize"), row))
            if section["type"] != 8:  # SHT_NOBITS has no file bytes.
                checked_slice(data, section["offset"], section["size"])
            self.sections.append(section)
        names = self.section_bytes(strings_index)
        for section in self.sections:
            section["name"] = self.string(names, section["name_offset"])

    @staticmethod
    def string(data, offset):
        require(0 <= offset < len(data), "string outside table")
        end = data.find(b"\0", offset)
        require(end >= 0, "unterminated string")
        return data[offset:end].decode()

    def section_bytes(self, index):
        require(0 <= index < len(self.sections), "section index outside table")
        s = self.sections[index]
        require(s["type"] != 8, "NOBITS has no file bytes")
        return checked_slice(self.data, s["offset"], s["size"])

    def section_named(self, name):
        rows = [(i, s) for i, s in enumerate(self.sections) if s["name"] == name]
        require(len(rows) == 1, "expected one section: " + name)
        return rows[0]

    def function(self, name):
        found = []
        for symbols in self.sections:
            if symbols["type"] != 2:  # Deliberately use full .symtab, not dynsym duplicates.
                continue
            require(symbols["entsize"] == 24 and symbols["size"] % 24 == 0,
                    "bad symbol table shape")
            strings = self.section_bytes(symbols["link"])
            for at in range(symbols["offset"], symbols["offset"] + symbols["size"], 24):
                n, info, _, index, value, size = struct.unpack_from("<IBBHQQ", self.data, at)
                if self.string(strings, n) != name or info & 15 != 2 or not size:
                    continue
                require(0 < index < len(self.sections), "function has no ordinary section")
                section = self.sections[index]
                relative = value if self.kind == 1 else value - section["addr"]
                require(section["flags"] & 4 and relative >= 0 and
                        relative + size <= section["size"], "function outside executable section")
                offset = section["offset"] + relative
                found.append(dict(symbol=name, section=index, section_name=section["name"],
                                  section_relative_offset=relative, offset=offset, bytes=size,
                                  sha256=digest(checked_slice(self.data, offset, size))))
        require(len(found) == 1, "expected one nonempty function: " + name)
        return found[0]

    def object_relocations(self, function):
        require(self.kind == 1, "object relocations require ET_REL")
        result = []
        for section in self.sections:
            if section["type"] not in (4, 9) or section["info"] != function["section"]:
                continue
            stride = 24 if section["type"] == 4 else 16
            require(section["entsize"] == stride and section["size"] % stride == 0,
                    "bad relocation table shape")
            for at in range(section["offset"], section["offset"] + section["size"], stride):
                offset, info = struct.unpack_from("<QQ", self.data, at)
                relative = offset - function["section_relative_offset"]
                if 0 <= relative < function["bytes"]:
                    result.append(dict(offset=relative, type=info & 0xffffffff, symbol_index=info >> 32))
        return result


def body(elf, function):
    return checked_slice(elf.data, function["offset"], function["bytes"])


def analyze(package=HERE, repo=REPO):
    provenance = read_json(package / "provenance.json")
    for name, expected in provenance["external_inputs"].items():
        data = local_path(repo, name).read_bytes()
        require(len(data) == expected["bytes"] and digest(data) == expected["sha256"],
                "changed external input: " + name)
    obj = Elf((package / "core.rcgu.o").read_bytes())
    require((obj.kind, obj.machine, obj.flags) == (1, 263, 0), "unexpected object ELF header")
    function = obj.function(provenance["symbol"])
    code = body(obj, function)
    relocs = obj.object_relocations(function)
    require(not relocs, "fmt write has object relocations")
    require(len(code) % 8 == 0, "unaligned SBF code")
    calls = [at for at in range(0, len(code), 8) if code[at:at+2] == b"\x85\x10"]
    require(not calls, "fmt write has relative call immediates")
    selected = read_json(repo / provenance["selected_helpers"])
    linked = {}
    for version, folder in provenance["builds"].items():
        metadata = selected[version]["helpers"]["core_fmt_write"]
        stripped = Elf((local_path(repo, folder) / "pump_fees_candidate.so").read_bytes())
        symbols = Elf((local_path(repo, folder) / "unstripped.so").read_bytes())
        _, text = stripped.section_named(".text")
        symbol_text, _ = symbols.section_named(".text")
        require(stripped.data[text["offset"]:text["offset"] + text["size"]] ==
                symbols.section_bytes(symbol_text), "stripped/unstripped text differs")
        symbol, = metadata["names"]
        f = symbols.function(symbol)
        linked_body = body(symbols, f)
        require((f["offset"], f["bytes"], f["sha256"]) ==
                (metadata["candidate_start"], metadata["bytes"], metadata["raw_sha256"]),
                "prior helper record differs from symbol bytes")
        # Here text file offsets match across the retained stripped/unstripped pair.
        require(checked_slice(stripped.data, f["offset"], f["bytes"]) == linked_body,
                "stripped helper offset differs")
        linked[version] = dict(symbol=symbol, offset=f["offset"], bytes=len(linked_body),
                               sha256=digest(linked_body), raw_equals_shipped_object=linked_body == code)
    capture = Elf((repo / provenance["capture"]).read_bytes())
    prior = selected["v144-build-01"]["helpers"]["core_fmt_write"]
    match, = prior["matches"]
    start, size = match["original_start"], prior["bytes"]
    _, text = capture.section_named(".text")
    require(text["offset"] <= start and start + size <= text["offset"] + text["size"],
            "captured window outside text")
    captured = checked_slice(capture.data, start, size)
    require(digest(captured) == prior["raw_sha256"], "captured/v144 raw comparison changed")
    hits = []
    at = text["offset"]
    while (at := capture.data.find(code, at, text["offset"] + text["size"])) >= 0:
        hits.append(at)
        at += 1
    return dict(object_function=function, object_relocations=relocs, relative_calls=calls,
                builds=linked, captured_window=dict(offset=start, bytes=size, sha256=digest(captured),
                raw_equals_shipped_object=captured == code, raw_equals_v144=True),
                shipped_body_exact_occurrences_in_captured_text=hits,
                normalized_comparisons=0, compiler_executions=0, unique_historical_compiler_proved=False)


def check_archive(path, package=HERE, repo=REPO):
    """Reacquisition check. Hash first, then stream; never extract or execute files."""
    provenance = read_json(package / "provenance.json")
    expected = provenance["asset"]
    with path.open("rb") as stream:
        actual_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    require(path.stat().st_size == expected["bytes"] and actual_hash == expected["sha256"],
            "release archive size/digest mismatch")
    manifest = read_json(repo / provenance["distribution_manifest"])
    rows = {row["path"]: row for row in manifest}
    require(len(rows) == len(manifest), "duplicate distribution manifest paths")
    # The historical manifest hashes the installed ld.lld after dereferencing it.
    # Validate the one observed alias in-memory; never create/follow filesystem links.
    aliases = {"llvm/bin/ld.lld": "llvm/bin/lld"}
    require(set(aliases) <= set(rows), "expected linker alias missing from manifest")
    wanted = set(rows) | set(aliases.values()) | {"version.md"}
    seen = set()
    resolved_links = []
    obj_checked = False
    with tarfile.open(path, mode="r|bz2") as archive:
        for member in archive:
            name = member.name.removeprefix("./")
            if name not in wanted:
                continue
            require(name not in seen, "duplicate selected tar member: " + name)
            seen.add(name)
            if name in aliases:
                require(member.issym() and member.linkname == "lld", "unexpected linker alias")
                resolved_links.append(dict(path=name, linkname=member.linkname, target=aliases[name]))
                continue
            require(member.isfile(), "nonregular selected tar member: " + name)
            stream = archive.extractfile(member)
            require(stream is not None, "missing tar payload")
            if name == provenance["rlib"]["path"]:
                raw = stream.read()
                checksum = digest(raw)
                member_rows = [row for row in ar_members(raw) if row[0] == provenance["object"]["member"]]
                require(len(member_rows) == 1, "missing ar object")
                _, offset, payload = member_rows[0]
                require(offset == provenance["object"]["member_offset"], "ar member offset mismatch")
                require(payload == (package / "core.rcgu.o").read_bytes(), "release object differs")
                obj_checked = True
            elif name == "version.md":
                raw = stream.read()
                require(raw == (package / "version.md").read_bytes(), "version file differs")
                continue
            else:
                checksum = hashlib.file_digest(stream, "sha256").hexdigest()
            key = next((alias for alias, target in aliases.items() if target == name), name)
            require(member.size == rows[key]["bytes"] and checksum == rows[key]["sha256"],
                    "distribution member differs: " + name)
    require(seen == wanted and obj_checked, "release archive missing selected inputs")
    return dict(archive_sha256=actual_hash, selected_distribution_files_verified=len(rows),
                version_md_verified=True, retained_object_equals_archive_member=True,
                in_memory_resolved_links=resolved_links)


def verify(package=HERE, repo=REPO):
    manifest = read_json(package / "manifest.json")
    actual = {p.relative_to(package).as_posix() for p in package.rglob("*")
              if p.is_file() and "__pycache__" not in p.parts and p.name != "manifest.json"}
    require(actual == set(manifest), "package file set differs")
    for name, sha in manifest.items():
        require(digest(local_path(package, name).read_bytes()) == sha, "changed package input: " + name)
    provenance = read_json(package / "provenance.json")
    asset = provenance["asset"]
    release = read_json(package / "release-metadata.json")
    row, = [row for row in release["assets"] if row["id"] == asset["id"]]
    require((row["name"], row["size"], row["digest"], row["browser_download_url"]) ==
            (asset["name"], asset["bytes"], "sha256:" + asset["sha256"], asset["url"]),
            "publisher receipt differs")
    raw = (package / "core.rcgu.o").read_bytes()
    require(len(raw) == provenance["object"]["bytes"] and digest(raw) == provenance["object"]["sha256"],
            "retained object identity differs")
    distribution = read_json(repo / provenance["distribution_manifest"])
    rlib, = [row for row in distribution if row["path"] == provenance["rlib"]["path"]]
    require(rlib == provenance["rlib"], "rlib identity differs from prior manifest")
    receipt = read_json(package / "download-receipt.json")
    require(receipt["exit"] == 0 and receipt["asset_id"] == asset["id"] and
            receipt["bytes"] == asset["bytes"] and receipt["sha256"] == asset["sha256"] and
            receipt["url"] == asset["url"], "download receipt differs")
    observed = analyze(package, repo)
    require(observed == read_json(package / "analysis.json"), "analysis differs from saved result")
    require(observed["builds"]["v1461-build-01"]["raw_equals_shipped_object"] and
            observed["builds"]["v146-build-01"]["raw_equals_shipped_object"] and
            not observed["captured_window"]["raw_equals_shipped_object"] and
            not observed["shipped_body_exact_occurrences_in_captured_text"], "unexpected comparison result")
    import cross_program
    cross = cross_program.analyze(package, repo)
    require(cross == read_json(package / "cross-program-analysis.json"), "cross-program analysis differs")
    require(set(cross["captures"]) == {"pump", "pump_amm", "pump_fees"}, "unexpected capture set")
    for capture in cross["captures"].values():
        occurrences = capture["helper_occurrences"]
        require(not occurrences["v1461_fmt_write"], "unexpected shipped fmt body occurrence")
        for name in ("v144_core_fmt_write", "v144_integer_entry"):
            matches = occurrences[name]
            require(len(matches) == 1 and matches[0]["instruction_aligned"] and
                    matches[0]["occupies_complete_direct_call_window"] and
                    not matches[0]["loader_relocations"], "unexpected v144 helper boundary/relocations")
    import v144
    positive = v144.analyze(package, repo)
    require(positive == read_json(package / "v144/analysis.json"), "v144 object analysis differs")
    return dict(verified=True, object_to_link_raw_identity=True, captured_window_raw_identity=False,
                archive_to_object_rechecked=False, historical_compiler_identified=False,
                cross_program_captures=3, raw_v144_call_bounded_windows=6,
                v144_shipped_generic_bodies=positive["positive_generic_object_bodies"],
                v144_archive_to_object_rechecked=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="optional official Darwin arm64 v1.46.1 tar.bz2")
    parser.add_argument("--v144-archive", type=Path, help="optional official Darwin arm64 v1.44 tar.bz2")
    args = parser.parse_args()
    result = verify()
    if args.archive:
        result["archive_validation"] = check_archive(args.archive)
        result["archive_to_object_rechecked"] = True
    if args.v144_archive:
        import v144
        result["v144_archive_validation"] = v144.check_archive(args.v144_archive)
        result["v144_archive_to_object_rechecked"] = True
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
