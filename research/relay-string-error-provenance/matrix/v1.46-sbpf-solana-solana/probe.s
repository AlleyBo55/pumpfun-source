	.text
	.file	"relay_typeid_probe.37774a21d3adc3ca-cgu.0"
	.section	".text._ZN4core3ptr205drop_in_place$LT$$LT$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Send$u2b$core..marker..Sync$GT$$u20$as$u20$core..convert..From$LT$alloc..string..String$GT$$GT$..from..StringError$GT$17h68706c042b2681d9E","ax",@progbits
	.p2align	3
	.type	_ZN4core3ptr205drop_in_place$LT$$LT$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Send$u2b$core..marker..Sync$GT$$u20$as$u20$core..convert..From$LT$alloc..string..String$GT$$GT$..from..StringError$GT$17h68706c042b2681d9E,@function
_ZN4core3ptr205drop_in_place$LT$$LT$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Send$u2b$core..marker..Sync$GT$$u20$as$u20$core..convert..From$LT$alloc..string..String$GT$$GT$..from..StringError$GT$17h68706c042b2681d9E:
	ldxdw r2, [r1 + 0]
	jeq r2, 0, LBB0_2
	ldxdw r1, [r1 + 8]
	mov64 r3, 1
	call __rust_dealloc
LBB0_2:
	exit
.Lfunc_end0:
	.size	_ZN4core3ptr205drop_in_place$LT$$LT$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Send$u2b$core..marker..Sync$GT$$u20$as$u20$core..convert..From$LT$alloc..string..String$GT$$GT$..from..StringError$GT$17h68706c042b2681d9E, .Lfunc_end0-_ZN4core3ptr205drop_in_place$LT$$LT$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Send$u2b$core..marker..Sync$GT$$u20$as$u20$core..convert..From$LT$alloc..string..String$GT$$GT$..from..StringError$GT$17h68706c042b2681d9E

	.section	.text._ZN4core5error5Error5cause17h1f4b9d7fd21fe0aeE,"ax",@progbits
	.p2align	3
	.type	_ZN4core5error5Error5cause17h1f4b9d7fd21fe0aeE,@function
_ZN4core5error5Error5cause17h1f4b9d7fd21fe0aeE:
	stdw [r1 + 0], 0
	exit
.Lfunc_end1:
	.size	_ZN4core5error5Error5cause17h1f4b9d7fd21fe0aeE, .Lfunc_end1-_ZN4core5error5Error5cause17h1f4b9d7fd21fe0aeE

	.section	.text._ZN4core5error5Error7provide17h528eff5e9ffd9872E,"ax",@progbits
	.p2align	3
	.type	_ZN4core5error5Error7provide17h528eff5e9ffd9872E,@function
_ZN4core5error5Error7provide17h528eff5e9ffd9872E:
	exit
.Lfunc_end2:
	.size	_ZN4core5error5Error7provide17h528eff5e9ffd9872E, .Lfunc_end2-_ZN4core5error5Error7provide17h528eff5e9ffd9872E

	.section	.text._ZN4core5error5Error7type_id17h2c429f7296e4ef91E,"ax",@progbits
	.p2align	3
	.type	_ZN4core5error5Error7type_id17h2c429f7296e4ef91E,@function
_ZN4core5error5Error7type_id17h2c429f7296e4ef91E:
	lddw r2, 4696683940124548206
	stxdw [r1 + 8], r2
	lddw r2, -2177860845394207463
	stxdw [r1 + 0], r2
	exit
.Lfunc_end3:
	.size	_ZN4core5error5Error7type_id17h2c429f7296e4ef91E, .Lfunc_end3-_ZN4core5error5Error7type_id17h2c429f7296e4ef91E

	.section	.text.io_error_type_id,"ax",@progbits
	.globl	io_error_type_id
	.p2align	3
	.type	io_error_type_id,@function
io_error_type_id:
	lddw r2, 1028161430631072222
	stxdw [r1 + 8], r2
	lddw r2, -3260020417342916134
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
	call _ZN5alloc7raw_vec12handle_error17h568ce53ef95b3793E
LBB5_2:
	lddw r1, 8246126623413003634
	stxdw [r7 + 0], r1
	stw [r7 + 7], 1700949874
	mov64 r1, 24
	mov64 r2, 8
	call __rust_alloc
	jne r0, 0, LBB5_4
	mov64 r1, 8
	mov64 r2, 24
	call _ZN5alloc5alloc18handle_alloc_error17h6a12f0428b99bff1E
LBB5_4:
	stxdw [r0 + 8], r7
	stdw [r0 + 16], 11
	stdw [r0 + 0], 11
	lddw r1, .L__unnamed_1
	stxdw [r6 + 8], r1
	stxdw [r6 + 0], r0
	exit
.Lfunc_end5:
	.size	boxed_string_error, .Lfunc_end5-boxed_string_error

	.type	.L__unnamed_2,@object
	.section	.rodata..L__unnamed_2,"a",@progbits
.L__unnamed_2:
	.ascii	"relay probe"
	.size	.L__unnamed_2, 11

	.type	.L__unnamed_3,@object
	.section	.data.rel.ro..L__unnamed_3,"aw",@progbits
	.p2align	3, 0x0
.L__unnamed_3:
	.quad	_ZN4core3ptr205drop_in_place$LT$$LT$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Send$u2b$core..marker..Sync$GT$$u20$as$u20$core..convert..From$LT$alloc..string..String$GT$$GT$..from..StringError$GT$17h68706c042b2681d9E
	.asciz	"\030\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_ZN223_$LT$$LT$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Send$u2b$core..marker..Sync$GT$$u20$as$u20$core..convert..From$LT$alloc..string..String$GT$$GT$..from..StringError$u20$as$u20$core..fmt..Display$GT$3fmt17ha18a5cc0de379cc0E
	.size	.L__unnamed_3, 32

	.type	.L__unnamed_1,@object
	.section	.data.rel.ro..L__unnamed_1,"aw",@progbits
	.p2align	3, 0x0
.L__unnamed_1:
	.quad	_ZN4core3ptr205drop_in_place$LT$$LT$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Send$u2b$core..marker..Sync$GT$$u20$as$u20$core..convert..From$LT$alloc..string..String$GT$$GT$..from..StringError$GT$17h68706c042b2681d9E
	.asciz	"\030\000\000\000\000\000\000\000\b\000\000\000\000\000\000"
	.quad	_ZN221_$LT$$LT$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Send$u2b$core..marker..Sync$GT$$u20$as$u20$core..convert..From$LT$alloc..string..String$GT$$GT$..from..StringError$u20$as$u20$core..fmt..Debug$GT$3fmt17h080759d0838f9fe6E
	.quad	_ZN223_$LT$$LT$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Send$u2b$core..marker..Sync$GT$$u20$as$u20$core..convert..From$LT$alloc..string..String$GT$$GT$..from..StringError$u20$as$u20$core..fmt..Display$GT$3fmt17ha18a5cc0de379cc0E
	.quad	.L__unnamed_3
	.quad	_ZN4core5error5Error5cause17h1f4b9d7fd21fe0aeE
	.quad	_ZN4core5error5Error7type_id17h2c429f7296e4ef91E
	.quad	_ZN223_$LT$$LT$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Send$u2b$core..marker..Sync$GT$$u20$as$u20$core..convert..From$LT$alloc..string..String$GT$$GT$..from..StringError$u20$as$u20$core..error..Error$GT$11description17h356b0e643c6c87e8E
	.quad	_ZN4core5error5Error5cause17h1f4b9d7fd21fe0aeE
	.quad	_ZN4core5error5Error7provide17h528eff5e9ffd9872E
	.size	.L__unnamed_1, 88

