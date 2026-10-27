#!/usr/bin/env python3
"""Materialize active program sources plus the behavioral recovery overlay into a scratch tree."""
import argparse
import os
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[2]
OVERLAY = pathlib.Path(__file__).resolve().parent / 'programs'
PROGRAMS = ('pump', 'mayhem')


def under(path, directory):
    """True if path is directory or inside it, by file identity (case-insensitive filesystems included)."""
    if not directory.exists():
        return False
    existing = next(p for p in (path, *path.parents) if p.exists())
    return any(os.path.samefile(p, directory) for p in (existing, *existing.parents))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=pathlib.Path, default=ROOT / 'work/behavioral-recovery')
    args = parser.parse_args()
    target = args.target.resolve()
    if under(target, ROOT) and not under(target, ROOT / 'work'):
        parser.error('target must be outside the repository or under work/; active source is never modified')
    if target.exists():
        parser.error(f'{target} already exists')
    for name in PROGRAMS:
        shutil.copytree(ROOT / 'programs' / name, target / 'programs' / name, ignore=shutil.ignore_patterns('target'))
    replaced = []
    for source in sorted(OVERLAY.rglob('*')):
        if source.is_file():
            relative = source.relative_to(OVERLAY)
            destination = target / 'programs' / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            replaced.append(str(relative))
    print(f'materialized {", ".join(PROGRAMS)} into {target}')
    for path in replaced:
        print(f'  overlay: programs/{path}')


if __name__ == '__main__':
    main()
