	.text
	.file	"relay_typeid_probe.e44b228785be53d5-cgu.0"
	.section	".text._ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17haf0766698fe186bfE","ax",@progbits
	.p2align	3
	.type	_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17haf0766698fe186bfE,@function
_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17haf0766698fe186bfE:
	ldxdw r2, [r1 + 0]
	jeq r2, 0, LBB0_2
	ldxdw r1, [r1 + 8]
	mov64 r3, 1
	call __rust_dealloc
LBB0_2:
	exit
.Lfunc_end0:
	.size	_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17haf0766698fe186bfE, .Lfunc_end0-_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17haf0766698fe186bfE

	.section	.text._ZN4core5error5Error5cause17h3348537b6822bf47E,"ax",@progbits
	.p2align	3
	.type	_ZN4core5error5Error5cause17h3348537b6822bf47E,@function
_ZN4core5error5Error5cause17h3348537b6822bf47E:
	stdw [r1 + 0], 0
	exit
.Lfunc_end1:
	.size	_ZN4core5error5Error5cause17h3348537b6822bf47E, .Lfunc_end1-_ZN4core5error5Error5cause17h3348537b6822bf47E

	.section	.text._ZN4core5error5Error7provide17h797d92f8e778c728E,"ax",@progbits
	.p2align	3
	.type	_ZN4core5error5Error7provide17h797d92f8e778c728E,@function
_ZN4core5error5Error7provide17h797d92f8e778c728E:
	exit
.Lfunc_end2:
	.size	_ZN4core5error5Error7provide17h797d92f8e778c728E, .Lfunc_end2-_ZN4core5error5Error7provide17h797d92f8e778c728E

	.section	.text._ZN4core5error5Error7type_id17hf795ce7cd48789c4E,"ax",@progbits
	.p2align	3
	.type	_ZN4core5error5Error7type_id17hf795ce7cd48789c4E,@function
_ZN4core5error5Error7type_id17hf795ce7cd48789c4E:
	lddw r2, -8309907005259863666
	stxdw [r1 + 8], r2
	lddw r2, 5218528593773829779
	stxdw [r1 + 0], r2
	exit
.Lfunc_end3:
	.size	_ZN4core5error5Error7type_id17hf795ce7cd48789c4E, .Lfunc_end3-_ZN4core5error5Error7type_id17hf795ce7cd48789c4E

	.section	.text.io_error_type_id,"ax",@progbits
	.globl	io_error_type_id
	.p2align	3
	.type	io_error_type_id,@function
io_error_type_id:
	lddw r2, 731535434808256210
	stxdw [r1 + 8], r2
	lddw r2, 7851131396452564835
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
	jne r7, 0, LBB5_2
	mov64 r1, 1
	mov64 r2, 11
	lddw r3, .L__unnamed_1
	call _ZN5alloc7raw_vec12handle_error17h446a779b52f4f50dE
LBB5_2:
	lddw r1, 8246126623413003634
	stxdw [r7 + 0], r1
	stw [r7 + 7], 1700949874
	mov64 r1, 24
	mov64 r2, 8
	call __rust_alloc
	jeq r0, 0, LBB5_4
	stxdw [r0 + 8], r7
	stdw [r0 + 16], 11
	stdw [r0 + 0], 11
	lddw r1, .L__unnamed_2
	stxdw [r6 + 8], r1
	stxdw [r6 + 0], r0
	exit
LBB5_4:
	mov64 r1, 8
	mov64 r2, 24
	call _ZN5alloc5alloc18handle_alloc_error17h80defc2166b4708fE
.Lfunc_end5:
	.size	boxed_string_error, .Lfunc_end5-boxed_string_error

	.type	.L__unnamed_3,@object
	.section	.rodata..L__unnamed_3,"a",@progbits
.L__unnamed_3:
	.ascii	"/home/runner/work/platform-tools/platform-tools/out/rust/library/alloc/src/slice.rs"
	.size	.L__unnamed_3, 83

	.type	.L__unnamed_1,@object
	.section	.data.rel.ro..L__unnamed_1,"aw",@progbits
	.p2align	3, 0x0
.L__unnamed_1:
	.quad	.L__unnamed_3
	.asciz	"S\000\000\000\000\000\000\000\237\000\000\000\031\000\000"
	.size	.L__unnamed_1, 24

	.type	.L__unnamed_4,@object
	.section	.rodata..L__unnamed_4,"a",@progbits
.L__unnamed_4:
	.ascii	"relay probe"
	.size	.L__unnamed_4, 11

	.type	.L__unnamed_5,@object
	.section	.data.rel.ro..L__unnamed_5,"aw",@progbits
	.p2align	3, 0x0
.L__unnamed_5:
	.quad	_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17haf0766698fe186bfE
	.asciz	"\030\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_ZN256_$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$u20$as$u20$core..fmt..Display$GT$3fmt17h673780fac7753329E
	.size	.L__unnamed_5, 32

	.type	.L__unnamed_2,@object
	.section	.data.rel.ro..L__unnamed_2,"aw",@progbits
	.p2align	3, 0x0
.L__unnamed_2:
	.quad	_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17haf0766698fe186bfE
	.asciz	"\030\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_ZN254_$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$u20$as$u20$core..fmt..Debug$GT$3fmt17h5c232ec1c4b281d8E
	.quad	_ZN256_$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$u20$as$u20$core..fmt..Display$GT$3fmt17h673780fac7753329E
	.quad	.L__unnamed_5
	.quad	_ZN4core5error5Error5cause17h3348537b6822bf47E
	.quad	_ZN4core5error5Error7type_id17hf795ce7cd48789c4E
	.quad	_ZN256_$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$u20$as$u20$core..error..Error$GT$11description17h82a8f32041d6019dE
	.quad	_ZN4core5error5Error5cause17h3348537b6822bf47E
	.quad	_ZN4core5error5Error7provide17h797d92f8e778c728E
	.size	.L__unnamed_2, 88

