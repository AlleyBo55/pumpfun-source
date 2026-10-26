// Dump every decoded instruction (address <tab> mnemonic/operands) to the file
// named by env REA_DUMP_OUT. Used as an independent oracle for our own sBPF
// disassembler. Read-only; no program mutation.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import java.io.FileWriter;
import java.io.PrintWriter;

public class DumpText extends GhidraScript {
    public void run() throws Exception {
        String out = System.getenv("REA_DUMP_OUT");
        if (out == null) out = "/tmp/ghidra_text_dump.tsv";
        PrintWriter w = new PrintWriter(new FileWriter(out));
        Listing l = currentProgram.getListing();
        long base = currentProgram.getImageBase().getOffset();
        w.println("# imagebase=0x" + Long.toHexString(base));
        InstructionIterator it = l.getInstructions(true);
        long count = 0;
        while (it.hasNext()) {
            Instruction in = it.next();
            w.println(in.getAddress() + "\t" + in.toString());
            count++;
        }
        w.close();
        println("DumpText wrote " + count + " instructions to " + out);
    }
}
