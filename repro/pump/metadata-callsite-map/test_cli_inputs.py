"""Synthetic CLI/classification checks; no ELF reader or original is opened."""
from pathlib import Path
import ast, subprocess, sys, tempfile, unittest
TOOL = Path(__file__).with_name('meta_map.py')
class AdmissionTests(unittest.TestCase):
    def cli(self, root, original, output):
        reader=root/'reader.py';reader.write_text("raise RuntimeError('READER_MUST_NOT_IMPORT')")
        symbols=root/'symbols';symbols.write_bytes(b'SYNTHETIC')
        catalog=root/'catalog';catalog.write_text('{}')
        return subprocess.run([sys.executable,'-B',str(TOOL),'--elf-reader',str(reader),'--original',str(original),'--symbols',str(symbols),'--catalog',str(catalog),'--output',str(output)],capture_output=True,text=True)
    def test_missing_input_fails_before_reader_import(self):
        with tempfile.TemporaryDirectory()as t:
            r=Path(t);result=self.cli(r,r/'missing',r/'fresh')
            self.assertEqual(result.returncode,2);self.assertIn('missing explicit input',result.stderr);self.assertNotIn('READER_MUST_NOT_IMPORT',result.stderr)
    def test_existing_output_fails_before_reader_import(self):
        with tempfile.TemporaryDirectory()as t:
            r=Path(t);original=r/'original';original.write_bytes(b'SYNTHETIC');output=r/'old';output.write_text('PRESERVE')
            result=self.cli(r,original,output)
            self.assertEqual(result.returncode,2);self.assertIn('must be fresh',result.stderr);self.assertEqual(output.read_text(),'PRESERVE');self.assertNotIn('READER_MUST_NOT_IMPORT',result.stderr)
    def classify(self, on, cn):
        tree=ast.parse(TOOL.read_text())
        function=next((n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='classify'),None)
        if function is not None:
            namespace={};exec(compile(ast.Module(body=[function],type_ignores=[]),'<synthetic-classifier>','exec'),namespace)
            value=namespace['classify'](on,cn)
            return value is True or value=='metadata_only'
        # Map tool's inline guard is extracted without executing its input/reader code.
        loop=next(n for n in tree.body if isinstance(n,ast.For)and any(isinstance(x,ast.Assign)and any(isinstance(y,ast.Name)and y.id=='diffs'for y in x.targets)for x in n.body))
        guard=next(n.test for n in loop.body if isinstance(n,ast.If)and ast.unparse(n.test).startswith('not diffs'))
        rejected=eval(compile(ast.Expression(body=guard),'<synthetic-map-filter>','eval'),{'on':on,'cn':cn,'diffs':[i for i in range(len(on))if on[i]!=cn[i]]})
        return not rejected
    def test_store_immediate_difference_is_only_heuristic(self):
        self.assertTrue(self.classify(bytes([0x62,0,0,0,1,0,0,0]),bytes([0x62,0,0,0,2,0,0,0])))
    def test_store_operand_difference_is_not_metadata(self):
        self.assertFalse(self.classify(bytes([0x62,0,0,0,1,0,0,0]),bytes([0x62,1,0,0,1,0,0,0])))
if __name__=='__main__':unittest.main()
