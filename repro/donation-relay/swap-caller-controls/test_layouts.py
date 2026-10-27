import unittest
from pathlib import Path
from verify import layouts


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.log = (Path(__file__).parent / "builds/layout-probe/build.log").read_text()

    def test_recorded_layout_offsets(self):
        result = layouts(self.log)
        fields = {
            f["name"]: f["offset"]
            for f in result["anchor_framework::JustSwapV1<'_>"]["fields"]
        }
        self.assertEqual(
            {
                name: fields[name]
                for name in ["mint", "signer", "token_program", "distribution"]
            },
            {"mint": 296, "signer": 320, "token_program": 328, "distribution": 440},
        )
        burn = result["settlement_handlers::BurnCloseContext<'_>"]
        self.assertEqual([f["offset"] for f in burn["fields"]], [0, 48, 96, 144, 192])

    def test_inconsistent_size_rejected(self):
        with self.assertRaises(AssertionError):
            layouts(
                self.log.replace(
                    "`settlement_handlers::BurnCloseContext<'_>`: 240 bytes",
                    "`settlement_handlers::BurnCloseContext<'_>`: 241 bytes",
                )
            )

    def test_missing_type_rejected(self):
        with self.assertRaises(AssertionError):
            layouts(
                self.log.replace(
                    "settlement_handlers::BurnCloseContext", "missing::Type"
                )
            )

    def test_unknown_layout_line_rejected(self):
        with self.assertRaises(AssertionError):
            layouts(
                self.log.replace(
                    "print-type-size     field `.token`: 48 bytes",
                    "print-type-size     unknown `.token`: 48 bytes",
                )
            )


if __name__ == "__main__":
    unittest.main()
