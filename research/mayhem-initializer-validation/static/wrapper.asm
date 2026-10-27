
/comparison/deployed.so:	file format elf64-sbf

Disassembly of section .text:

0000000000000120 <.text>:
   80ef0: bf 37 00 00 00 00 00 00      	mov64 r7, r3
   80ef8: bf 28 00 00 00 00 00 00      	mov64 r8, r2
   80f00: bf 16 00 00 00 00 00 00      	mov64 r6, r1
   80f08: 18 01 00 00 0b e1 0a 00 00 00 00 00 00 00 00 00      	lddw r1, 0xae10b
   80f18: b7 02 00 00 22 00 00 00      	mov64 r2, 0x22
   80f20: 85 10 00 00 ff ff ff ff      	call -0x1
   80f28: 62 0a fc f9 ff ff ff ff      	stw [r10 - 0x604], -0x1
   80f30: 7b 7a 08 fa 00 00 00 00      	stxdw [r10 - 0x5f8], r7
   80f38: 7b 8a 00 fa 00 00 00 00      	stxdw [r10 - 0x600], r8
   80f40: bf a1 00 00 00 00 00 00      	mov64 r1, r10
   80f48: 07 01 00 00 fc f9 ff ff      	add64 r1, -0x604
   80f50: 7b 1a 08 f0 00 00 00 00      	stxdw [r10 - 0xff8], r1
   80f58: bf a1 00 00 00 00 00 00      	mov64 r1, r10
   80f60: 07 01 00 00 08 fd ff ff      	add64 r1, -0x2f8
   80f68: bf a3 00 00 00 00 00 00      	mov64 r3, r10
   80f70: 07 03 00 00 00 fa ff ff      	add64 r3, -0x600
   80f78: bf a5 00 00 00 00 00 00      	mov64 r5, r10
   80f80: bf 62 00 00 00 00 00 00      	mov64 r2, r6
   80f88: 85 10 00 00 6d d0 ff ff      	call -0x2f93
   80f90: 61 a7 08 fd 00 00 00 00      	ldxw r7, [r10 - 0x2f8]
   80f98: 55 07 03 00 02 00 00 00      	jne r7, 0x2, +0x3 <.text+0x80e98>
   80fa0: 79 a1 18 fd 00 00 00 00      	ldxdw r1, [r10 - 0x2e8]
   80fa8: 79 a0 10 fd 00 00 00 00      	ldxdw r0, [r10 - 0x2f0]
   80fb0: 05 00 1f 00 00 00 00 00      	ja +0x1f <.text+0x80f90>
   80fb8: 61 a1 0c fd 00 00 00 00      	ldxw r1, [r10 - 0x2f4]
   80fc0: 7b 1a f0 f9 00 00 00 00      	stxdw [r10 - 0x610], r1
   80fc8: 79 a9 10 fd 00 00 00 00      	ldxdw r9, [r10 - 0x2f0]
   80fd0: 79 a8 18 fd 00 00 00 00      	ldxdw r8, [r10 - 0x2e8]
   80fd8: bf a1 00 00 00 00 00 00      	mov64 r1, r10
   80fe0: 07 01 00 00 28 fa ff ff      	add64 r1, -0x5d8
   80fe8: bf a2 00 00 00 00 00 00      	mov64 r2, r10
   80ff0: 07 02 00 00 20 fd ff ff      	add64 r2, -0x2e0
   80ff8: b7 03 00 00 e0 02 00 00      	mov64 r3, 0x2e0
   81000: 85 10 00 00 b0 52 00 00      	call 0x52b0
   81008: 7b 8a 20 fa 00 00 00 00      	stxdw [r10 - 0x5e0], r8
   81010: 7b 9a 18 fa 00 00 00 00      	stxdw [r10 - 0x5e8], r9
   81018: 79 a1 f0 f9 00 00 00 00      	ldxdw r1, [r10 - 0x610]
   81020: 63 1a 14 fa 00 00 00 00      	stxw [r10 - 0x5ec], r1
   81028: 63 7a 10 fa 00 00 00 00      	stxw [r10 - 0x5f0], r7
   81030: 61 a1 fc f9 00 00 00 00      	ldxw r1, [r10 - 0x604]
   81038: 63 1a 28 fd 00 00 00 00      	stxw [r10 - 0x2d8], r1
   81040: 79 a1 08 fa 00 00 00 00      	ldxdw r1, [r10 - 0x5f8]
   81048: 7b 1a 20 fd 00 00 00 00      	stxdw [r10 - 0x2e0], r1
   81050: 79 a1 00 fa 00 00 00 00      	ldxdw r1, [r10 - 0x600]
   81058: 7b 1a 18 fd 00 00 00 00      	stxdw [r10 - 0x2e8], r1
   81060: bf a7 00 00 00 00 00 00      	mov64 r7, r10
   81068: 07 07 00 00 10 fa ff ff      	add64 r7, -0x5f0
   81070: 7b 7a 10 fd 00 00 00 00      	stxdw [r10 - 0x2f0], r7
   81078: 7b 6a 08 fd 00 00 00 00      	stxdw [r10 - 0x2f8], r6
   81080: bf a1 00 00 00 00 00 00      	mov64 r1, r10
   81088: 07 01 00 00 08 fd ff ff      	add64 r1, -0x2f8
   81090: 85 10 00 00 14 03 00 00      	call 0x314
   81098: bf 71 00 00 00 00 00 00      	mov64 r1, r7
   810a0: bf 62 00 00 00 00 00 00      	mov64 r2, r6
   810a8: 85 10 00 00 a8 d8 ff ff      	call -0x2758
   810b0: 95 00 00 00 00 00 00 00      	exit
