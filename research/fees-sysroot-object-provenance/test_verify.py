"""Mutation and parser checks; no network, toolchain execution, or blockchain calls."""
import io
import json
from pathlib import Path
import shutil
import struct
import tarfile
import tempfile
import unittest

import verify as v


def member(name, payload):
    header = (name.ljust(16) + "0".ljust(12) + "0".ljust(6) + "0".ljust(6) +
              "644".ljust(8) + str(len(payload)).ljust(10) + "`\n").encode()
    return header + payload + (b"\n" if len(payload) % 2 else b"")


class ArchiveTests(unittest.TestCase):
    def test_gnu_long_name_and_payload_offset(self):
        names = b"long-core-object-name.o/\n"
        data = b"!<arch>\n" + member("//", names) + member("/0", b"ELF")
        rows = list(v.ar_members(data))
        self.assertEqual(rows[1][0], "long-core-object-name.o")
        self.assertEqual(data[rows[1][1]:rows[1][1] + 3], b"ELF")

    def test_bsd_extended_name(self):
        data = b"!<arch>\n" + member("#1/5", b"foo.oBODY")
        name, offset, raw = list(v.ar_members(data))[0]
        self.assertEqual((name, raw, data[offset:offset + 4]), ("foo.o", b"BODY", b"BODY"))

    def test_duplicate_member_rejected(self):
        data = b"!<arch>\n" + member("a/", b"x") * 2
        with self.assertRaisesRegex(ValueError, "duplicate"):
            list(v.ar_members(data))

    def test_malformed_archives_rejected(self):
        samples = [b"!<thin>\n", b"!<arch>\n" + b"x" * 10,
                   b"!<arch>\n" + member("/9", b"x"),
                   (b"!<arch>\n" + member("a/", b"x"))[:-1]]
        for data in samples:
            with self.subTest(data=data[:10]), self.assertRaises(ValueError):
                list(v.ar_members(data))


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.provenance = v.read_json(v.HERE / "provenance.json")
        cls.raw = (v.HERE / "core.rcgu.o").read_bytes()
        cls.elf = v.Elf(cls.raw)
        cls.function = cls.elf.function(cls.provenance["symbol"])

    def test_saved_raw_relationships(self):
        actual = v.analyze()
        self.assertEqual(actual, v.read_json(v.HERE / "analysis.json"))
        self.assertTrue(actual["builds"]["v1461-build-01"]["raw_equals_shipped_object"])
        self.assertFalse(actual["captured_window"]["raw_equals_shipped_object"])
        self.assertEqual(actual["shipped_body_exact_occurrences_in_captured_text"], [])

    def test_full_package(self):
        self.assertTrue(v.verify()["verified"])

    def test_instruction_mutation_changes_raw_identity(self):
        mutated = bytearray(self.raw)
        mutated[self.function["offset"] + 16] ^= 1
        after = v.Elf(bytes(mutated)).function(self.provenance["symbol"])
        self.assertNotEqual(after["sha256"], self.function["sha256"])

    def test_missing_symbol_rejected(self):
        with self.assertRaisesRegex(ValueError, "expected one"):
            self.elf.function("not-the-real-symbol")

    def test_truncated_elf_and_invalid_section_table_rejected(self):
        bad = bytearray(self.raw)
        struct.pack_into("<Q", bad, 40, len(bad) + 1)
        for raw in [self.raw[:40], self.raw[:-1], bytes(bad)]:
            with self.subTest(length=len(raw)), self.assertRaises(ValueError):
                v.Elf(raw)

    def test_new_relocation_is_detected(self):
        index, section = next((i, s) for i, s in enumerate(self.elf.sections)
                              if s["type"] in (4, 9) and s["size"] >= 16)
        bad = bytearray(self.raw)
        table = struct.unpack_from("<Q", bad, 40)[0]
        struct.pack_into("<I", bad, table + index * 64 + 44, self.function["section"])
        struct.pack_into("<Q", bad, section["offset"], self.function["section_relative_offset"])
        changed = v.Elf(bytes(bad))
        self.assertTrue(changed.object_relocations(changed.function(self.provenance["symbol"])))

    def test_external_input_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            first = next(iter(self.provenance["external_inputs"]))
            target = repo / first
            target.parent.mkdir(parents=True)
            target.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "changed external input"):
                v.analyze(repo=repo)

    def test_retained_object_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            package = Path(td) / "packet"
            shutil.copytree(v.HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            raw = bytearray((package / "core.rcgu.o").read_bytes())
            raw[self.function["offset"]] ^= 1
            (package / "core.rcgu.o").write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "changed package input: core.rcgu.o"):
                v.verify(package=package)

    def test_unsafe_input_paths_rejected(self):
        for path in ["../outside", "/absolute", "C:/absolute", "a\\b", "a//b"]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                v.local_path(v.HERE, path)


class ReleaseArchiveTests(unittest.TestCase):
    """Tiny digest-bound archive fixtures exercise the full optional archive path."""
    def fixture(self, root, *, linkname="lld", duplicate=False, changed_object=False):
        package = root / "package"
        package.mkdir()
        repo = root / "repo"
        repo.mkdir()
        rlib = b"!<arch>\n" + member("core.o/", b"OBJECT")
        (package / "core.rcgu.o").write_bytes(b"OTHER" if changed_object else b"OBJECT")
        (package / "version.md").write_bytes(b"VERSION")
        rows = [{"path": "libcore.rlib", "bytes": len(rlib), "sha256": v.digest(rlib)},
                {"path": "llvm/bin/ld.lld", "bytes": 3, "sha256": v.digest(b"LLD")}]
        (repo / "distribution.json").write_text(json.dumps(rows))
        archive = root / "release.tar.bz2"
        with tarfile.open(archive, "w:bz2") as out:
            for name, payload in [("llvm/bin/lld", b"LLD"), ("libcore.rlib", rlib), ("version.md", b"VERSION")]:
                info = tarfile.TarInfo(name)
                info.size = len(payload)
                out.addfile(info, io.BytesIO(payload))
                if duplicate and name == "libcore.rlib":
                    out.addfile(info, io.BytesIO(payload))
            info = tarfile.TarInfo("llvm/bin/ld.lld")
            info.type = tarfile.SYMTYPE
            info.linkname = linkname
            out.addfile(info)
        provenance = dict(asset=dict(bytes=archive.stat().st_size, sha256=v.digest(archive.read_bytes())),
                          distribution_manifest="distribution.json", rlib=dict(path="libcore.rlib"),
                          object=dict(member="core.o", member_offset=68))
        (package / "provenance.json").write_text(json.dumps(provenance))
        return archive, package, repo

    def test_complete_stream_and_alias_check(self):
        with tempfile.TemporaryDirectory() as td:
            archive, package, repo = self.fixture(Path(td))
            result = v.check_archive(archive, package, repo)
            self.assertEqual(result["selected_distribution_files_verified"], 2)
            self.assertTrue(result["retained_object_equals_archive_member"])
            self.assertFalse((package / "llvm").exists())

    def test_archive_tampering_rejected_before_parsing(self):
        with tempfile.TemporaryDirectory() as td:
            archive, package, repo = self.fixture(Path(td))
            with archive.open("ab") as out:
                out.write(b"x")
            with self.assertRaisesRegex(ValueError, "size/digest mismatch"):
                v.check_archive(archive, package, repo)

    def test_outside_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            archive, package, repo = self.fixture(Path(td), linkname="../../../outside")
            with self.assertRaisesRegex(ValueError, "unexpected linker alias"):
                v.check_archive(archive, package, repo)

    def test_duplicate_selected_member_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            archive, package, repo = self.fixture(Path(td), duplicate=True)
            with self.assertRaisesRegex(ValueError, "duplicate selected tar member"):
                v.check_archive(archive, package, repo)

    def test_different_retained_object_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            archive, package, repo = self.fixture(Path(td), changed_object=True)
            with self.assertRaisesRegex(ValueError, "release object differs"):
                v.check_archive(archive, package, repo)


if __name__ == "__main__":
    unittest.main()
