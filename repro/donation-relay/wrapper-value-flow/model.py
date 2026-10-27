"""Restricted caller value-flow model, not a general emulator or equivalence proof.

Input-address expressions are distinct unless syntactically identical. Overflow
paths are excluded explicitly. Callee effects use the documented summaries.
Unknown instructions, uninitialized local memory and clobbered register reads
fail closed. All symbolic bytes and expressions are retained in the report.
"""

import hashlib
import json
import struct

NODES = {}


def token(expr):
    data = json.dumps(expr, separators=(",", ":"))
    h = hashlib.sha256(data.encode()).hexdigest()
    assert h not in NODES or NODES[h] == expr
    NODES[h] = expr
    return h


class Val:
    def __init__(self, bs, ptr=None):
        assert len(bs) == 8
        self.bs = tuple(bs)
        self.ptr = ptr

    def number(self):
        return (
            int.from_bytes(bytes(self.bs), "little")
            if all(isinstance(x, int) for x in self.bs)
            else None
        )

    def addr(self):
        return self.ptr or ("value:" + token(list(self.bs)), 0)

    def add(self, n):
        if self.number() is not None:
            return integer(self.number() + n)
        base, off = self.addr()
        return pointer(base, off + n)


def integer(n):
    return Val((n % (1 << 64)).to_bytes(8, "little"))


def pointer(base, off=0):
    return Val([token(["pointer", base, off, i]) for i in range(8)], (base, off))


class Registers(dict):
    def __getitem__(self, key):
        value = super().__getitem__(key)
        assert value is not None, ("undefined register", key)
        return value


def trace(elf, start, size, ords, mode):
    assert mode in ("success", "error")
    memory = {}
    ptrs = {}
    regs = Registers({i: None for i in range(11)})
    for i, name in [
        (1, "result"),
        (2, "accounts"),
        (3, "args"),
        (4, "epoch-bump"),
        (5, "debouncer-bump"),
        (10, "stack"),
    ]:
        regs[i] = pointer(name)

    def load(address, width):
        base, off = address.addr()
        if base in ("stack", "result"):
            assert all((base, off + i) in memory for i in range(width)), (
                "uninitialized memory",
                base,
                off,
                width,
            )
        bs = [
            memory[(base, off + i)]
            if (base, off + i) in memory
            else token(["input-memory", base, off + i])
            for i in range(width)
        ]
        bs += [0] * (8 - width)
        return Val(bs, ptrs.get(tuple(bs)))

    def store(address, value, width):
        base, off = address.addr()
        for i in range(width):
            memory[(base, off + i)] = value.bs[i]
        if width == 8 and value.ptr:
            ptrs[value.bs] = value.ptr

    def image(address, size):
        return [load(address.add(i), 1).bs[0] for i in range(size)]

    pc = 0
    steps = 0
    assumptions = []
    calls = []
    boundary = None
    while True:
        assert 0 <= pc < size and steps < 10000, (pc, steps)
        steps += 1
        op, r, off, imm = struct.unpack("<BBhi", elf.at(start + pc, 8))
        dst = r & 15
        src = r >> 4
        nextpc = pc + 8
        if op == 0xBF:
            regs[dst] = regs[src]
        elif op == 0xB7:
            regs[dst] = integer(imm)
        elif op == 0x07:
            regs[dst] = regs[dst].add(imm)
        elif op in (0x79, 0x61, 0x69, 0x71):
            regs[dst] = load(
                regs[src].add(off), {0x79: 8, 0x61: 4, 0x69: 2, 0x71: 1}[op]
            )
        elif op in (0x7A, 0x62, 0x6A, 0x72):
            store(
                regs[dst].add(off),
                integer(imm),
                {0x7A: 8, 0x62: 4, 0x6A: 2, 0x72: 1}[op],
            )
        elif op == 0x18:
            assert start + pc not in elf.relocations
            assert elf.at(start + pc + 8, 4) == bytes(4)
            hi = struct.unpack("<I", elf.at(start + pc + 12, 4))[0]
            regs[dst] = integer((imm & 0xFFFFFFFF) + (hi << 32))
            nextpc += 8
        elif op == 0x95:
            assert boundary is not None
            return dict(
                calls=calls,
                assumptions=assumptions,
                boundary=boundary,
                output=image(pointer("result"), 153 if mode == "success" else 24),
                steps=steps,
            )
        elif op in (0x7B, 0x63, 0x6B, 0x73):
            store(
                regs[dst].add(off), regs[src], {0x7B: 8, 0x63: 4, 0x6B: 2, 0x73: 1}[op]
            )
        elif op == 0x05:
            nextpc = pc + 8 + off * 8
        elif op in (0x15, 0x55):
            n = regs[dst].number()
            if n is None:
                assert op == 0x15 and imm == 0, (pc, op, imm)
                prior_add = struct.unpack("<BBhi", elf.at(start + pc - 16, 8))
                prior_flag = struct.unpack("<BBhi", elf.at(start + pc - 8, 8))
                assert (
                    prior_add == (0x07, dst, 0, 1)
                    and prior_flag[0] == 0xB7
                    and prior_flag[3] == 1
                ), ("unsupported symbolic branch", pc)
                assumptions.append(
                    dict(
                        offset=pc,
                        condition="increment by one did not wrap to zero",
                        value=list(regs[dst].bs),
                    )
                )
                take = False
            else:
                take = (
                    (n == (imm % (1 << 64))) if op == 0x15 else (n != (imm % (1 << 64)))
                )
            if take:
                nextpc = pc + 8 + off * 8
        elif op == 0x85:
            assert src == 1 and start + pc not in elf.relocations, (
                pc,
                "external call reached",
            )
            target = start + pc + 8 + imm * 8
            which = ords.get(target, [])
            calls.append(dict(offset=pc, target=target, ordinals=which))
            if which == [112]:
                active = list(range(32)) + [
                    j + i for j in (32, 80, 128, 176) for i in range(43)
                ]
                args = image(regs[3], 68)
                boundary = dict(
                    context={i: load(regs[2].add(i), 1).bs[0] for i in active},
                    arguments=args,
                )
                store(regs[1], integer(0 if mode == "success" else 1), 8)
                for i in range(8, 40):
                    store(
                        regs[1].add(i),
                        Val([token(["shared-result", mode, i])] + [0] * 7),
                        1,
                    )
            elif 389 in which:
                payload = image(regs[2], 24)
                for i in range(24):
                    store(
                        regs[1].add(i),
                        Val([token(["string-clone-output", payload, i])] + [0] * 7),
                        1,
                    )
            elif 473 in which:
                count = regs[3].number()
                assert count is not None
                values = image(regs[2], count)
                for i, v in enumerate(values):
                    store(regs[1].add(i), Val([v] + [0] * 7), 1)
            else:
                raise AssertionError((pc, target, which))
            for i in range(6):
                regs[i] = None
        else:
            raise AssertionError((pc, hex(op)))
        pc = nextpc
