"""Reproduce the whitespace-only alignment of two observed error origins."""
import re


def align(source):
    needle = 'Err(error!(FeeError::DeprecatedInstruction))'
    first, program = source.index(needle), source.index('#[program]')
    output, offset, removed = [], 0, 0
    for line in source[:first].splitlines(keepends=True):
        if offset >= program and line.endswith('\n') and not line.strip():
            removed += 1
        else:
            output.append(line)
        offset += len(line)
    result = ''.join(output) + source[first:]
    remaining = result[:result.index(needle)].count('\n') + 1 - 183
    folded = []
    for name in ('get_fees_with_quote_mint', 'update_fee_config', 'get_fees',
                 'upsert_fee_tiers', 'upsert_stable_fee_tiers'):
        if remaining == 0:
            break
        start = result.index('    pub fn ' + name + '(')
        end = result.index('\n    }', start) + len('\n    }')
        body = result[start:end]
        assert start < result.index(needle)
        # These five retained bodies contain no quoted tokens or comments.
        assert all(marker not in body for marker in ('"', "'", '//', '/*'))
        count = min(remaining, body.count('\n'))
        replacement, actual = re.subn(r'\n[ \t]*', ' ', body, count=count)
        assert actual == count
        result = result[:start] + replacement + result[end:]
        remaining -= count
        folded.append(dict(method=name, removed_newlines=count))
    assert remaining == 0
    lines = [i for i, line in enumerate(result.splitlines(), 1) if needle in line]
    assert lines == [183, 188]
    return result, dict(removed_blank_lines=removed, folded_methods=folded,
                        deprecated_macro_lines=lines)
