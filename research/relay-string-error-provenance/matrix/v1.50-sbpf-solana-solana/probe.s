	.text
	.file	"relay_typeid_probe.e44b228785be53d5-cgu.0"
	.section	".text._ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17hdd5b3b8c1bbc95a6E","ax",@progbits
	.p2align	3
	.type	_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17hdd5b3b8c1bbc95a6E,@function
_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17hdd5b3b8c1bbc95a6E:
	ldxdw r2, [r1 + 0]
	jeq r2, 0, LBB0_2
	ldxdw r1, [r1 + 8]
	mov64 r3, 1
	call __rust_dealloc
LBB0_2:
	exit
.Lfunc_end0:
	.size	_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17hdd5b3b8c1bbc95a6E, .Lfunc_end0-_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17hdd5b3b8c1bbc95a6E

	.section	.text._ZN4core5error5Error5cause17h033443960bd736b5E,"ax",@progbits
	.p2align	3
	.type	_ZN4core5error5Error5cause17h033443960bd736b5E,@function
_ZN4core5error5Error5cause17h033443960bd736b5E:
	stdw [r1 + 0], 0
	exit
.Lfunc_end1:
	.size	_ZN4core5error5Error5cause17h033443960bd736b5E, .Lfunc_end1-_ZN4core5error5Error5cause17h033443960bd736b5E

	.section	.text._ZN4core5error5Error7provide17h46c8539eabc3f110E,"ax",@progbits
	.p2align	3
	.type	_ZN4core5error5Error7provide17h46c8539eabc3f110E,@function
_ZN4core5error5Error7provide17h46c8539eabc3f110E:
	exit
.Lfunc_end2:
	.size	_ZN4core5error5Error7provide17h46c8539eabc3f110E, .Lfunc_end2-_ZN4core5error5Error7provide17h46c8539eabc3f110E

	.section	.text._ZN4core5error5Error7type_id17hb35b87cd8729eeeaE,"ax",@progbits
	.p2align	3
	.type	_ZN4core5error5Error7type_id17hb35b87cd8729eeeaE,@function
_ZN4core5error5Error7type_id17hb35b87cd8729eeeaE:
	lddw r2, -1370918573024367643
	stxdw [r1 + 8], r2
	lddw r2, -6809438839394813014
	stxdw [r1 + 0], r2
	exit
.Lfunc_end3:
	.size	_ZN4core5error5Error7type_id17hb35b87cd8729eeeaE, .Lfunc_end3-_ZN4core5error5Error7type_id17hb35b87cd8729eeeaE

	.section	.text.io_error_type_id,"ax",@progbits
	.globl	io_error_type_id
	.p2align	3
	.type	io_error_type_id,@function
io_error_type_id:
	lddw r2, 8748334695015199108
	stxdw [r1 + 8], r2
	lddw r2, -4921838239903218999
	stxdw [r1 + 0], r2
	exit
.Lfunc_end4:
	.size	io_error_type_id, .Lfunc_end4-io_error_type_id

	.section	.text.boxed_string_error,"ax",@progbits
	.globl	boxed_string_error
	.p2align	3
	.type	boxed_string_error,@function
boxed_string_error:
	mov64 r6, r1
	mov64 r1, 11
	mov64 r2, 1
	call __rust_alloc
	mov64 r7, r0
	jeq r7, 0, LBB5_3
	lddw r1, 8246126623413003634
	stxdw [r7 + 0], r1
	stw [r7 + 7], 1700949874
	mov64 r1, 24
	mov64 r2, 8
	call __rust_alloc
	jeq r0, 0, LBB5_2
	stxdw [r0 + 8], r7
	stdw [r0 + 16], 11
	stdw [r0 + 0], 11
	lddw r1, .L__unnamed_1
	stxdw [r6 + 8], r1
	stxdw [r6 + 0], r0
	exit
LBB5_3:
	mov64 r1, 1
	mov64 r2, 11
	lddw r3, .L__unnamed_2
	call _ZN5alloc7raw_vec12handle_error17h0fd52313375ec35bE
LBB5_2:
	mov64 r1, 8
	mov64 r2, 24
	call _ZN5alloc5alloc18handle_alloc_error17h4dbdc578804d63d9E
.Lfunc_end5:
	.size	boxed_string_error, .Lfunc_end5-boxed_string_error

	.type	.L__unnamed_3,@object
	.section	.rodata..L__unnamed_3,"a",@progbits
.L__unnamed_3:
	.ascii	"/Users/runner/work/platform-tools/platform-tools/out/rust/library/alloc/src/slice.rs"
	.size	.L__unnamed_3, 84

	.type	.L__unnamed_2,@object
	.section	.data.rel.ro..L__unnamed_2,"aw",@progbits
	.p2align	3, 0x0
.L__unnamed_2:
	.quad	.L__unnamed_3
	.asciz	"T\000\000\000\000\000\000\000\237\000\000\000\031\000\000"
	.size	.L__unnamed_2, 24

	.type	.L__unnamed_4,@object
	.section	.rodata..L__unnamed_4,"a",@progbits
.L__unnamed_4:
	.ascii	"relay probe"
	.size	.L__unnamed_4, 11

	.type	.L__unnamed_5,@object
	.section	.data.rel.ro..L__unnamed_5,"aw",@progbits
	.p2align	3, 0x0
.L__unnamed_5:
	.quad	_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17hdd5b3b8c1bbc95a6E
	.asciz	"\030\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_ZN256_$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$u20$as$u20$core..fmt..Display$GT$3fmt17hbc7130e8f9026000E
	.size	.L__unnamed_5, 32

	.type	.L__unnamed_1,@object
	.section	.data.rel.ro..L__unnamed_1,"aw",@progbits
	.p2align	3, 0x0
.L__unnamed_1:
	.quad	_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17hdd5b3b8c1bbc95a6E
	.asciz	"\030\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_ZN254_$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$u20$as$u20$core..fmt..Debug$GT$3fmt17h5870d68e0372ec98E
	.quad	_ZN256_$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$u20$as$u20$core..fmt..Display$GT$3fmt17hbc7130e8f9026000E
	.quad	.L__unnamed_5
	.quad	_ZN4core5error5Error5cause17h033443960bd736b5E
	.quad	_ZN4core5error5Error7type_id17hb35b87cd8729eeeaE
	.quad	_ZN256_$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$u20$as$u20$core..error..Error$GT$11description17hbe404b9ec567d619E
	.quad	_ZN4core5error5Error5cause17h033443960bd736b5E
	.quad	_ZN4core5error5Error7provide17h46c8539eabc3f110E
	.size	.L__unnamed_1, 88

