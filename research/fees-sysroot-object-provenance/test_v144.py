"""Positive sysroot provenance and rejection of changed archive associations."""
import gzip
import io
import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest
import verify as v
import v144
from test_verify import member


def save(path, value):
    path.write_text(json.dumps(value), encoding='utf-8')


class ObjectEvidenceTests(unittest.TestCase):
    def test_positive_aliases_and_extended_variants(self):
        result = v144.analyze()
        self.assertEqual(result, v.read_json(v.HERE / 'v144/analysis.json'))
        self.assertEqual(sum(r['raw_equals_linked_reference'] for r in result['objects']), 4)
        self.assertFalse(result['generic_target_alias_distinguished'])
        self.assertFalse(result['unique_historical_compiler_proved'])

    def test_relative_call_decoder_skips_lddw_continuation(self):
        code = b'\x18' + bytes(7) + b'\x85\x10' + bytes(6) + b'\x85\x10' + bytes(6)
        self.assertEqual(v144.relative_calls(code), [16])
        with self.assertRaisesRegex(ValueError, 'truncated LDDW'):
            v144.relative_calls(b'\x18' + bytes(7))

    def test_changed_expected_function_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / 'packet'
            shutil.copytree(v.HERE, dest, ignore=shutil.ignore_patterns('__pycache__'))
            p = v.read_json(dest / 'v144/provenance.json')
            p['objects'][0]['function']['offset'] += 8
            save(dest / 'v144/provenance.json', p)
            with self.assertRaisesRegex(ValueError, 'symbol differs'):
                v144.analyze(dest)

    def test_archive_is_not_claimed_rechecked_by_default(self):
        result = v.verify()
        self.assertFalse(result['v144_archive_to_object_rechecked'])
        self.assertEqual(result['v144_shipped_generic_bodies'], 4)


class ArchiveBindingTests(unittest.TestCase):
    def fixture(self, root, *, changed_member=False, duplicate=False, symlink=False):
        package = root / 'packet'
        packet = package / 'v144'
        packet.mkdir(parents=True)
        selected, rows, blobs, rlibs = [], [], {}, {}
        for i in range(10):
            raw = b'OBJECT' + bytes([i])
            digest = v.digest(raw)
            name = 'lib' + str(i) + '.rlib'
            blobs[digest + '.o'] = raw
            ar = b'!<arch>\n' + member('input.o/', b'CHANGED' if changed_member and i == 0 else raw)
            rlibs[name] = ar
            selected.append(dict(path=name, bytes=len(ar), sha256=v.digest(ar)))
            rows.append(dict(rlib=name, object_sha256=digest, object_bytes=len(raw),
                             object_member='input.o', object_offset=68))
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode='w') as archive:
            for name, raw in blobs.items():
                info = tarfile.TarInfo(name); info.size = len(raw)
                archive.addfile(info, io.BytesIO(raw))
        (packet / 'objects.tar.gz').write_bytes(gzip.compress(buffer.getvalue()))
        (packet / 'version.md').write_bytes(b'VERSION')
        path = root / 'release.tar.bz2'
        with tarfile.open(path, 'w:bz2') as archive:
            for name, raw in dict(rlibs, **{'version.md': b'VERSION'}).items():
                info = tarfile.TarInfo('./' + name)
                if symlink and name == 'lib0.rlib':
                    info.type = tarfile.SYMTYPE; info.linkname = 'elsewhere'
                    archive.addfile(info)
                    continue
                info.size = len(raw)
                archive.addfile(info, io.BytesIO(raw))
                if duplicate and name == 'lib0.rlib':
                    archive.addfile(info, io.BytesIO(raw))
        p = dict(asset=dict(bytes=path.stat().st_size, sha256=v.digest(path.read_bytes())),
                 selected_rlibs=selected, objects=rows)
        save(packet / 'provenance.json', p)
        return path, package

    def test_all_ten_rlib_associations(self):
        with tempfile.TemporaryDirectory() as td:
            path, package = self.fixture(Path(td))
            result = v144.check_archive(path, package)
            self.assertEqual(result['complete_objects_equal_archive_members'], 10)
            self.assertFalse(result['publisher_digest_available'])

    def test_changed_object_rejected_even_with_updated_archive_digest(self):
        with tempfile.TemporaryDirectory() as td:
            path, package = self.fixture(Path(td), changed_member=True)
            with self.assertRaisesRegex(ValueError, 'archive object differs'):
                v144.check_archive(path, package)

    def test_duplicate_member_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path, package = self.fixture(Path(td), duplicate=True)
            with self.assertRaisesRegex(ValueError, 'duplicate or nonregular'):
                v144.check_archive(path, package)

    def test_link_in_place_of_selected_payload_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path, package = self.fixture(Path(td), symlink=True)
            with self.assertRaisesRegex(ValueError, 'duplicate or nonregular'):
                v144.check_archive(path, package)

    def test_changed_archive_digest_rejected_before_parse(self):
        with tempfile.TemporaryDirectory() as td:
            path, package = self.fixture(Path(td))
            path.write_bytes(b'invalid archive')
            with self.assertRaisesRegex(ValueError, 'size/digest differs'):
                v144.check_archive(path, package)


if __name__ == '__main__':
    unittest.main()
