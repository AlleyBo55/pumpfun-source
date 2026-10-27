
evidence/original/pump_fees/deployed.so:	file format elf64-sbf

Disassembly of section .text:

0000000000000120 <.text>:
    8907:	79 23 08 00 00 00 00 00	ldxdw r3, [r2 + 0x8]
    8908:	55 03 0e 00 00 00 00 00	jne r3, 0x0, +0xe <.text+0x115b8>
    8909:	bf a2 00 00 00 00 00 00	mov64 r2, r10
    8910:	07 02 00 00 f0 ff ff ff	add64 r2, -0x10
    8911:	bf 16 00 00 00 00 00 00	mov64 r6, r1
    8912:	bf 21 00 00 00 00 00 00	mov64 r1, r2
    8913:	b7 02 00 00 bd 0b 00 00	mov64 r2, 0xbbd
    8914:	85 10 00 00 4b 3d 01 00	call 0x13d4b
    8915:	79 a1 f0 ff 00 00 00 00	ldxdw r1, [r10 - 0x10]
    8916:	79 a2 f8 ff 00 00 00 00	ldxdw r2, [r10 - 0x8]
    8917:	7b 26 10 00 00 00 00 00	stxdw [r6 + 0x10], r2
    8918:	7b 16 08 00 00 00 00 00	stxdw [r6 + 0x8], r1
    8919:	18 01 00 00 00 00 00 00 00 00 00 00 00 00 00 80	lddw r1, -0x8000000000000000
    8921:	7b 16 00 00 00 00 00 00	stxdw [r6 + 0x0], r1
    8922:	05 00 08 00 00 00 00 00	ja +0x8 <.text+0x115f8>
    8923:	07 03 00 00 ff ff ff ff	add64 r3, -0x1
    8924:	7b 32 08 00 00 00 00 00	stxdw [r2 + 0x8], r3
    8925:	79 23 00 00 00 00 00 00	ldxdw r3, [r2 + 0x0]
    8926:	bf 34 00 00 00 00 00 00	mov64 r4, r3
    8927:	07 04 00 00 30 00 00 00	add64 r4, 0x30
    8928:	7b 42 00 00 00 00 00 00	stxdw [r2 + 0x0], r4
    8929:	bf 32 00 00 00 00 00 00	mov64 r2, r3
    8930:	85 10 00 00 ba ee ff ff	call -0x1146
    8931:	95 00 00 00 00 00 00 00	exit
