# standards/distribution/ — index

Distribution governs how dev-playbook's checks reach the governed repos —
the published hook, the roster, dogfooding, and the pinned rev.
The reasoning behind the rules is
[Distribution Explanation](/standards/distribution/explanation.md).

Ordering: its Standards.

- [Distribution Channel](/standards/distribution/channel.md) — How the hook repository's checks reach the governed repos — a publisher's local block and a consumer's pinned rev
- [Distribution Explanation](/standards/distribution/explanation.md) — The thinking behind the distribution rules — one published hook id, why enrollment rides the pin, the roster, why dev-playbook dogfoods its manifest instead of pinning, and why a stale pin is advisory
