"""Content-addressed seen-set: remember opaque keys, skip the ones seen before.

A key is an opaque string the caller computed; this library only remembers which
strings it has been told to remember. It never hashes, reads files, or
canonicalizes, and carries no domain vocabulary.
"""
