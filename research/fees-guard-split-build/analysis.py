"""Read-only raw ELF and FeeConfig helper comparison (no execution or masking)."""
import hashlib
import struct


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(raw):
    return {'bytes': len(raw), 'sha256': sha(raw)}


class Elf:
    def __init__(self, raw):
        self.raw = raw
        require(raw[:6] == b'\x7fELF\x02\x01', 'Expected little-endian ELF64')
        h = struct.unpack_from('<HHIQQQIHHHHHH', raw, 16)
        require(h[0] == 3 and h[1] in (247, 263) and h[10] == 64, 'Unexpected ELF header')
        require(h[11] > h[12] and h[5] + h[11]*64 <= len(raw), 'Invalid section table')
        rows = [struct.unpack_from('<IIQQQQIIQQ', raw, h[5]+i*64) for i in range(h[11])]
        strings = self.slice(rows[h[12]][4], rows[h[12]][5])
        self.sections = []
        for row in rows:
            name, kind, flags, address, offset, size, link, info, align, entsize = row
            require(name < len(strings), 'Invalid section name')
            self.sections.append(dict(name=strings[name:].split(b'\0', 1)[0].decode(), kind=kind,
                flags=flags, address=address, offset=offset, size=size, link=link, entsize=entsize))
        self.text = self.section('.text')
        self.symbols = []
        for section in self.sections:
            if section['kind'] != 2:
                continue
            require(section['entsize'] == 24 and section['size'] % 24 == 0, 'Invalid symbols')
            names = self.content(self.sections[section['link']])
            for offset in range(section['offset'], section['offset']+section['size'], 24):
                n, info, _, index, address, size = struct.unpack_from('<IBBHQQ', raw, offset)
                if info & 15 == 2 and index and size:
                    require(index < len(self.sections) and n < len(names), 'Invalid function symbol')
                    self.symbols.append(dict(name=names[n:].split(b'\0',1)[0].decode(),
                        address=address, size=size, section_index=index))

    def slice(self, offset, size):
        require(0 <= offset <= offset+size <= len(self.raw), 'Range outside ELF')
        return self.raw[offset:offset+size]

    def content(self, section):
        require(section['kind'] != 8, 'NOBITS has no file content')
        return self.slice(section['offset'], section['size'])

    def section(self, name):
        rows = [s for s in self.sections if s['name'] == name]
        require(len(rows) == 1, 'Section not unique: ' + name)
        return rows[0]

    def body(self, address, size):
        text = self.text
        require(text['address'] <= address and address+size <= text['address']+text['size'], 'Body outside text')
        return self.slice(text['offset']+address-text['address'], size)

    def allocated(self):
        return [dict(name=s['name'], address=s['address'], size=s['size'], flags=s['flags'],
                     sha256=sha(self.content(s)) if s['kind'] != 8 else None)
                for s in self.sections if s['flags'] & 2]


def instructions(raw, address):
    rows = []; offset = 0
    require(len(raw) % 8 == 0, 'Instruction body must contain complete slots')
    while offset < len(raw):
        op, regs, displacement, immediate = struct.unpack_from('<BBhi', raw, offset)
        width = 16 if op == 0x18 else 8
        require(offset+width <= len(raw), 'Truncated LDDW')
        pc = address + offset
        row = dict(relative_offset=offset, address=pc, opcode=op, destination=regs&15,
                   source=regs>>4, displacement=displacement, immediate=immediate,
                   raw=raw[offset:offset+width].hex())
        if op == 0x18:
            row['lddw_bytes'] = (raw[offset+4:offset+8]+raw[offset+12:offset+16]).hex()
        if op == 0x85 and regs>>4 == 1:
            row['encoded_call_target'] = pc+8+immediate*8
        elif op & 7 in (5, 6) and op not in (0x85, 0x95):
            row['branch_target'] = pc+8+displacement*8
        rows.append(row); offset += width
    return rows


DISCRIMINATOR = hashlib.sha256(b'account:FeeConfig').digest()[:8].hex()
ERROR = '0300000000000080'


def helper(elf):
    candidates = []
    for symbol in elf.symbols:
        if 'account16Account$LT$T$GT$8try_from' not in symbol['name']:
            continue
        rows = instructions(elf.body(symbol['address'], symbol['size']), symbol['address'])
        if any(r.get('lddw_bytes') == DISCRIMINATOR for r in rows):
            candidates.append(symbol)
    require(len(candidates) == 1, 'FeeConfig helper attribution not unique')
    return candidates[0]


def window(elf, start, size):
    raw = elf.body(start, size)
    rows = instructions(raw, start)
    calls = []
    for row in rows:
        if 'encoded_call_target' in row:
            calls.append(dict(address=row['address'], relative_offset=row['relative_offset'],
                target=row['encoded_call_target'], symbols=[s['name'] for s in elf.symbols
                    if s['address'] == row['encoded_call_target']]))
    return dict(address=start, **identity(raw),
        discriminator_sites=[r['address'] for r in rows if r.get('lddw_bytes') == DISCRIMINATOR],
        invalid_data_constant_sites=[r['address'] for r in rows if r.get('lddw_bytes') == ERROR],
        short_length_branches=[r for r in rows if r['opcode'] == 0xa5 and r['immediate'] == 8],
        encoded_calls=calls)


def raw_difference(a, b):
    return dict(raw_equal=a == b, common_length=min(len(a), len(b)),
                differing_positions_in_common_prefix=sum(x != y for x,y in zip(a,b)),
                unmatched_tail_bytes=abs(len(a)-len(b)))


def analyze(baseline_unstripped, baseline_stripped, split_unstripped, split_stripped, original):
    inputs = dict(baseline_unstripped=baseline_unstripped, baseline_stripped=baseline_stripped,
                  split_unstripped=split_unstripped, split_stripped=split_stripped, original=original)
    elfs = {k: Elf(v) for k,v in inputs.items()}
    windows = {}
    for phase in ('baseline', 'split'):
        elf, stripped = elfs[phase+'_unstripped'], elfs[phase+'_stripped']
        require(elf.allocated() == stripped.allocated(), 'Strip changed allocated content: '+phase)
        symbol = helper(elf)
        windows[phase] = dict(symbol=symbol['name'], **window(elf, symbol['address'], symbol['size']))
    original_elf = elfs['original']
    # Retest PR74's encoded query->wrapper->helper association. Original extent is inferred.
    query_calls = [r for r in instructions(original_elf.body(518976,1784),518976) if 'encoded_call_target' in r]
    require(query_calls[0]['encoded_call_target'] == 71256, 'Original query edge differs')
    wrapper_calls = [r for r in instructions(original_elf.body(71256,200),71256) if 'encoded_call_target' in r]
    require(wrapper_calls[-1]['encoded_call_target'] == 36072, 'Original helper edge differs')
    windows['original_inferred'] = window(original_elf,36072,1248)
    require(windows['original_inferred']['discriminator_sites'] == [36696], 'Original discriminator differs')
    return dict(scope='Raw ELF/helper comparison only; no normalization, execution, promotion or equivalence claim',
        inputs={k: identity(v) for k,v in inputs.items()},
        strip_preserves_allocated_sections=True,
        full_stripped_comparison=raw_difference(baseline_stripped,split_stripped),
        full_unstripped_comparison=raw_difference(baseline_unstripped,split_unstripped),
        allocated_sections={k: v.allocated() for k,v in elfs.items() if not k.endswith('_unstripped')},
        helpers=windows,
        helper_raw_comparison=raw_difference(elfs['baseline_stripped'].body(windows['baseline']['address'],windows['baseline']['bytes']),
            elfs['split_stripped'].body(windows['split']['address'],windows['split']['bytes'])),
        original_extent='1248-byte call-bounded inferred window from PR74, not a historical symbol proof',
        call_scope='Encoded relative CALL targets only; no loader/runtime proof')
