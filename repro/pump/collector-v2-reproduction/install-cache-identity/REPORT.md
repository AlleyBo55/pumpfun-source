# Current SDK install cache identities

A new read-only collection hashes the current local platform-tools v1.52 and Darwin Criterion v2.3.2 cache trees. Every regular file, link spelling and directory mode is recorded. File/link membership, mode, size, timestamp and inode metadata were stable across each collection. No compiler, SDK, target, downloader or original image ran or was acquired.

These are current observed local inputs. They do not authenticate an official release archive, prove historical presence, identify every actually loaded library, or retroactively close prior execution provenance. A future reviewed launcher must actually validate these pins before and after use and enforce its own offline boundary.
