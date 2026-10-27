	.file	"relay_typeid_probe.2f2b59c895ce6ae7-cgu.0"
	.section	".text._ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17hfff3dad81e7d2286E","ax",@progbits
	.p2align	3
	.type	_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17hfff3dad81e7d2286E,@function
_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17hfff3dad81e7d2286E:
	ldxdw r2, [r1 + 0]
	jeq r2, 0, LBB0_2
	ldxdw r1, [r1 + 8]
	mov64 r3, 1
	call _RNvCscR3e5J6VSLN_7___rustc14___rust_dealloc
LBB0_2:
	exit
.Lfunc_end0:
	.size	_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17hfff3dad81e7d2286E, .Lfunc_end0-_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17hfff3dad81e7d2286E

	.section	.text._ZN4core5error5Error5cause17h3de7045e00624405E,"ax",@progbits
	.p2align	3
	.type	_ZN4core5error5Error5cause17h3de7045e00624405E,@function
_ZN4core5error5Error5cause17h3de7045e00624405E:
	stdw [r1 + 0], 0
	exit
.Lfunc_end1:
	.size	_ZN4core5error5Error5cause17h3de7045e00624405E, .Lfunc_end1-_ZN4core5error5Error5cause17h3de7045e00624405E

	.section	.text._ZN4core5error5Error7provide17hbca6858b54b3570eE,"ax",@progbits
	.p2align	3
	.type	_ZN4core5error5Error7provide17hbca6858b54b3570eE,@function
_ZN4core5error5Error7provide17hbca6858b54b3570eE:
	exit
.Lfunc_end2:
	.size	_ZN4core5error5Error7provide17hbca6858b54b3570eE, .Lfunc_end2-_ZN4core5error5Error7provide17hbca6858b54b3570eE

	.section	.text._ZN4core5error5Error7type_id17hefb759ed922093dcE,"ax",@progbits
	.p2align	3
	.type	_ZN4core5error5Error7type_id17hefb759ed922093dcE,@function
_ZN4core5error5Error7type_id17hefb759ed922093dcE:
	lddw r2, -3345032770664817660
	stxdw [r1 + 8], r2
	lddw r2, 86750576918743129
	stxdw [r1 + 0], r2
	exit
.Lfunc_end3:
	.size	_ZN4core5error5Error7type_id17hefb759ed922093dcE, .Lfunc_end3-_ZN4core5error5Error7type_id17hefb759ed922093dcE

	.section	.text.io_error_type_id,"ax",@progbits
	.globl	io_error_type_id
	.p2align	3
	.type	io_error_type_id,@function
io_error_type_id:
	lddw r2, -8822651029840705707
	stxdw [r1 + 8], r2
	lddw r2, -4718039299650024297
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
	call _RNvCscR3e5J6VSLN_7___rustc35___rust_no_alloc_shim_is_unstable_v2
	mov64 r1, 11
	mov64 r2, 1
	call _RNvCscR3e5J6VSLN_7___rustc12___rust_alloc
	mov64 r7, r0
	jeq r7, 0, LBB5_3
	lddw r1, 8246126623413003634
	stxdw [r7 + 0], r1
	stw [r7 + 7], 1700949874
	call _RNvCscR3e5J6VSLN_7___rustc35___rust_no_alloc_shim_is_unstable_v2
	mov64 r1, 24
	mov64 r2, 8
	call _RNvCscR3e5J6VSLN_7___rustc12___rust_alloc
	jeq r0, 0, LBB5_4
	stxdw [r0 + 8], r7
	stdw [r0 + 16], 11
	stdw [r0 + 0], 11
	lddw r1, .Lanon.b620638706b261bc5fd111f38178867c.4
	stxdw [r6 + 8], r1
	stxdw [r6 + 0], r0
	exit
LBB5_3:
	mov64 r1, 1
	mov64 r2, 11
	lddw r3, .Lanon.b620638706b261bc5fd111f38178867c.1
	call _ZN5alloc7raw_vec12handle_error17hc915c5c16d0837b6E
LBB5_4:
	mov64 r1, 8
	mov64 r2, 24
	call _ZN5alloc5alloc18handle_alloc_error17h3ea6c81aa0aa0c6eE
.Lfunc_end5:
	.size	boxed_string_error, .Lfunc_end5-boxed_string_error

	.type	.Lanon.b620638706b261bc5fd111f38178867c.0,@object
	.section	.rodata.str1.1,"aMS",@progbits,1
.Lanon.b620638706b261bc5fd111f38178867c.0:
	.asciz	"/Users/runner/work/platform-tools/platform-tools/out/rust/library/alloc/src/slice.rs"
	.size	.Lanon.b620638706b261bc5fd111f38178867c.0, 85

	.type	.Lanon.b620638706b261bc5fd111f38178867c.1,@object
	.section	.data.rel.ro..Lanon.b620638706b261bc5fd111f38178867c.1,"aw",@progbits
	.p2align	3, 0x0
.Lanon.b620638706b261bc5fd111f38178867c.1:
	.quad	.Lanon.b620638706b261bc5fd111f38178867c.0
	.asciz	"U\000\000\000\000\000\000\000\301\001\000\000\035\000\000"
	.size	.Lanon.b620638706b261bc5fd111f38178867c.1, 24

	.type	.Lanon.b620638706b261bc5fd111f38178867c.2,@object
	.section	.rodata..Lanon.b620638706b261bc5fd111f38178867c.2,"a",@progbits
.Lanon.b620638706b261bc5fd111f38178867c.2:
	.ascii	"relay probe"
	.size	.Lanon.b620638706b261bc5fd111f38178867c.2, 11

	.type	.Lanon.b620638706b261bc5fd111f38178867c.3,@object
	.section	.data.rel.ro..Lanon.b620638706b261bc5fd111f38178867c.3,"aw",@progbits
	.p2align	3, 0x0
.Lanon.b620638706b261bc5fd111f38178867c.3:
	.quad	_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17hfff3dad81e7d2286E
	.asciz	"\030\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_ZN256_$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$u20$as$u20$core..fmt..Display$GT$3fmt17h846ae18baf50be73E
	.size	.Lanon.b620638706b261bc5fd111f38178867c.3, 32

	.type	.Lanon.b620638706b261bc5fd111f38178867c.4,@object
	.section	.data.rel.ro..Lanon.b620638706b261bc5fd111f38178867c.4,"aw",@progbits
	.p2align	3, 0x0
.Lanon.b620638706b261bc5fd111f38178867c.4:
	.quad	_ZN4core3ptr238drop_in_place$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$GT$17hfff3dad81e7d2286E
	.asciz	"\030\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_ZN254_$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$u20$as$u20$core..fmt..Debug$GT$3fmt17he08a6fea34b1676dE
	.quad	_ZN256_$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$u20$as$u20$core..fmt..Display$GT$3fmt17h846ae18baf50be73E
	.quad	.Lanon.b620638706b261bc5fd111f38178867c.3
	.quad	_ZN4core5error5Error5cause17h3de7045e00624405E
	.quad	_ZN4core5error5Error7type_id17hefb759ed922093dcE
	.quad	_ZN256_$LT$alloc..boxed..convert..$LT$impl$u20$core..convert..From$LT$alloc..string..String$GT$$u20$for$u20$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$GT$..from..StringError$u20$as$u20$core..error..Error$GT$11description17hc7c62571ef54cef2E
	.quad	_ZN4core5error5Error5cause17h3de7045e00624405E
	.quad	_ZN4core5error5Error7provide17hbca6858b54b3570eE
	.size	.Lanon.b620638706b261bc5fd111f38178867c.4, 88

