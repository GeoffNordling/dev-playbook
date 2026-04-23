# Accuracy audit of three spec-system docs

**The headline finding: your `oft-format.md` has the definitions of `Predated` and `Outdated` exactly swapped**, a bug that poisons every derived explanation (including the revision-bump paragraph and the incoming-status variants). Beyond that, `rfc2119.md` contains two silent word-drops in the SHOULD / SHOULD NOT definitions and a §6 paraphrase that downgrades an uppercase MUST to a lowercase "should," inverting the obligation strength the RFC self-applies. `ears.md` has mostly convention-vs-source mismatches plus one substantive structural claim (the generic template does not "directly permit" Complex) that is unsupported. RFC-paywall note: the RE'09 EARS paper was reached via a third-party mirror with IEEE watermark preserved, so both primary sources for EARS were verified in full.

The errors below are ordered by severity within each file. Gaps are deliberately short — only the things a practitioner relying solely on your doc would trip over.

---

## 1. `rfc2119.md` vs RFC 2119 + RFC 8174

### A. Errors

**1.1 The `MAY` interoperability block quote has the wrong period placement.** You wrote `"...for the feature the option provides)."` — period outside the parenthesis. RFC 2119 §5 actually reads `"...for the feature the option provides.)"` — period **inside** the parenthesis. The RFC's punctuation is genuinely unusual and you've silently normalized it. Because you present this as a verbatim block quote, every character is part of the claim.

**1.2 SHOULD definition drops the word "particular."** Your table says "valid reasons in particular circumstances to ignore **the item**." RFC 2119 §3 reads "to ignore **a particular item**." You dropped "particular" and changed "a" to "the." The rest of the sentence is copied exactly, so a reader will reasonably take your wording as authoritative.

**1.3 SHOULD NOT definition drops the same word.** Your table says "when **the behavior** is acceptable or even useful." RFC 2119 §4 reads "when **the particular behavior** is acceptable or even useful." Same failure mode as 1.2.

**1.4 §6 paraphrase downgrades an uppercase MUST to a lowercase "should," weakening the obligation.** You wrote "Imperatives **should** be used only where actually required for interoperation…" RFC 2119 §6 actually reads "they **MUST** only be used where it is actually required for interoperation…" This is the highest-stakes single error in the file: under the very vocabulary the RFC defines, lowercase "should" is a weaker obligation than uppercase MUST. The RFC is self-applying its own keywords here — that's the rhetorical point of the section — and your paraphrase loses it.

**1.5 "Interoperation" vs "interoperability" conflated.** Your second §6 sentence says "not required for **interoperation**." RFC 2119 §6 uses "**interoperability**" in that sentence (while using "interoperation" in the first). The RFC deliberately uses two different nouns; you collapse them.

**1.6 The "Informational vs. Standards Track" example is not in RFC 2119** (unwarranted-confidence error). The RFC's entire statement on document-level context is one abstract sentence: "Note that the force of these words is modified by the requirement level of the document in which they are used." It names no document categories, mentions neither "Informational" nor "Standards Track," and gives no example. You present a concrete Informational-vs-Standards-Track comparison as if it were part of the standard.

**1.7 Misattribution: the two opening "rules" are from RFC 8174, not RFC 2119.** Your file's H1 is "RFC 2119 — Obligation Vocabulary," and the two bullets under "Two rules govern application" are presented without attribution. But neither rule is in RFC 2119. The uppercase-only rule is RFC 8174 §2 ("The words have the meanings specified herein only when they are in all capitals… When these words are not capitalized, they have their normal English meanings and are not affected by this document"). The "use is optional" rule is also RFC 8174 §2 ("These words can be used as defined here, but using them is not required. Specifically, normative text does not require the use of these key words"). RFC 2119's abstract says only that the words are "often capitalized" — and that very ambiguity is why RFC 8174 exists.

**1.8 "Conforming documents embed this boilerplate verbatim" overstates the requirement.** RFC 8174 §2 uses lowercase "should incorporate this phrase" — a non-normative recommendation to authors *who choose to use the vocabulary*. The RFC does not use the word "verbatim," does not define conformance in terms of embedding, and does not require inclusion at all (using the key words is itself optional). You've elevated a lowercase "should" into a conformance-defining "verbatim" rule.

**1.9 Editorial additions that read as RFC text.** Two minor unwarranted-confidence errors in the §6 paragraph: "Imperative language has cost" is your gloss (not in RFC 2119), and "the canonical example is limiting retransmissions" upgrades the RFC's hedged "e.g., limiting retransmissions" to a "canonical" status the RFC does not grant.

### What is correct (verified)
The main RFC 8174 boilerplate block quote is character-for-character identical to the source (quote characters, commas, `"NOT RECOMMENDED"` included, `[RFC2119] [RFC8174]` bracket style, "when, and only when," comma placement). All five synonym pairings in your vocabulary table match RFC 2119 §§1–5. "BCP 14" correctly denotes the pair.

### B. Gaps worth closing
The single most material gap is that **RFC 8174 is never cited in prose** — readers cannot tell that the uppercase-only rule, the "use is optional" rule, and the inclusion of `NOT RECOMMENDED` in the key-word list are all RFC 8174 contributions updating RFC 2119. Secondary: RFC 2119 §5's vendor-choice framing for MAY (which motivates the interop rule) is dropped, and RFC 2119 §7's Security Considerations guidance — that the effects of MUST/SHOULD violations may be subtle and authors should elaborate them — is entirely absent.

---

## 2. `ears.md` vs Mavin RE'09 paper + alistairmavin.com/ears

*Source note: the IEEE Xplore landing page for RE'09 is paywalled, but the original IEEE-watermarked PDF is mirrored publicly and was read in full. Both primary sources were verified. Where they disagree (they do, non-trivially), it is called out.*

### A. Errors

**2.1 The Event-driven template is missing its precondition slot** (per the paper). Your row reads `WHEN <trigger>, the <system> shall <response>`. The paper §4.3 gives `WHEN <optional preconditions> <trigger> the <system name> shall <system response>` — parallel to the Unwanted-behaviour IF-THEN row where you *do* keep the precondition slot. Mavin's canonical site shows the simpler form without the slot, so you could defend alignment with the site — but then you'd also need to drop the precondition slot from the IF-THEN row. The inconsistency is the error: you picked one primary source's conventions for one pattern and the other's for another.

**2.2 "The generic template above permits Complex requirements directly" is unsupported by both primary sources.** The paper §4.1 defines exactly one optional-preconditions slot and one optional-trigger slot. Multi-keyword combinations like `While … when … if … then …` are introduced separately in §4.7 as a compositional rule, not as instantiations of the generic template. Mavin's site describes Complex the same way — as "combined" building blocks. Your framing presents a structural conclusion (the generic template permits Complex) that neither source draws.

**2.3 "Five patterns" contradicts Mavin's current canonical site.** The RE'09 paper lists five specialisations (§4.1) with Complex as a separate §4.7. But **Mavin's site lists six patterns under equal headings — Ubiquitous, State driven, Event driven, Optional feature, Unwanted behaviour, and Complex.** Mavin has promoted Complex to a peer. A doc claiming to "restate the standard" as five patterns without noting the site's six-pattern framing is contradicted by the more recent author-maintained reference.

**2.4 The all-caps keyword convention is paper-only.** You state "WHEN, WHILE, WHERE, IF…THEN are capitalized in the generic templates; actual requirement sentences use normal sentence case." The paper does this. **Mavin's site does not** — every generic template on the site uses sentence case (e.g., "While `<precondition(s)>`, the `<system name>` shall `<system response>`"; "If `<trigger>`, then the `<system name>` shall…"). Presenting the all-caps rule as the EARS convention is sourced to one primary, contradicted by the other.

**2.5 "Unwanted behavior" uses American spelling.** The paper §4.4 heading is "Unwanted behaviours" (British, plural). The site is "Unwanted behaviour requirements" (British, singular-attributive). Neither primary source uses the American spelling. Minor but worth correcting if you're restating a named pattern.

**2.6 "EARS covers sentence structure only" overstates Mavin's scope.** The paper (§2) explicitly says: "The work reported here is principally concerned with requirements syntax. Although measures were taken to improve the semantics of the requirements, they are not described in this paper." Semantic measures are out of scope of the paper's *exposition*, not out of scope of EARS. The site also frames EARS around quality, clarity, and ambiguity reduction — not pure structure.

**2.7 The RFC 2119 hand-off is your convention, not EARS.** "Obligation strength is handled by RFC 2119… the other concerns belong to whatever document format the requirement lives in" — neither primary source mentions RFC 2119, BCP 14, MUST/SHOULD/MAY, obligation strength, rationale, identity, or metadata scoping. Both sources mandate the single modal **"shall"** in every template with no alternatives. Your hand-off is a sensible local policy; it is not EARS.

**2.8 The IF-preconditions-vs-trigger gloss is interpretive.** You write that in the Unwanted-behaviour pattern, "preconditions scope when the trigger applies, while the trigger fires the response." The paper's §4.4 gives only the template and does not distinguish the slots semantically; its §4.7 example ("When selecting idle setting, if aircraft data is unavailable, then…") actually reads with the reverse scoping — the When-clause is the trigger and the If-clause is the unwanted precondition. The site's Unwanted-behaviour template has **no preconditions slot at all**. Your semantic story is plausible but unsourced and arguably contradicted by §4.7.

**2.9 `DURING` is paper-only** (not strictly an error, but worth the same caveat as 2.4). Paper §4.5 sanctions it explicitly ("the keyword During can be used instead of While… the meaning of During is identical to While"). Mavin's canonical site does not mention During anywhere.

### What is correct (verified)
The "temporal reading" claim for the generic-template ordering **is** sourced: paper §4.1 says "The order of the clauses in this syntax is also significant, since it follows temporal logic." The pattern names themselves (modulo 2.5 spelling) and the four core template shapes are accurately reproduced. The scope caveat ("targets high-level stakeholder requirements") matches paper §2's closing ("not… universally applicable to all levels of system decomposition. The technique is most suitable to the definition of high-level stakeholder requirements").

### B. Gaps worth closing
Mavin's site states an explicit multiplicity ruleset you don't mirror: **zero-or-many preconditions, zero-or-one trigger, one system name, one-or-many system responses** — a substantive conformance rule (e.g., only one trigger per requirement). Second: your doc never says EARS mandates the word **"shall"** as the modal, and because you delegate obligation strength to RFC 2119 (which does not use "shall" as a conformance keyword), a reader could wrongly infer that MUST/SHOULD/MAY substitute. Neither primary source supports that.

---

## 3. `oft-format.md` vs OpenFastTrace user guide (main)

### A. Errors

**3.1 `Predated` and `Outdated` are defined backwards — critical.** Your definitions: Predated = "link names a revision *older* than the upstream's current revision"; Outdated = "link names a revision *newer* than any revision the upstream has ever carried." The user guide's Outgoing Link Statuses table says the opposite: **"Predated | This item covers a *newer* revision of another item"** and **"Outdated | This item covers an *older* revision of another item."** Prose in the same section confirms: "When the outgoing link from this item is 'predated', that means it points to a newer version of the covered item than it should." The correct mapping is Predated = link revision **higher** than upstream (link is "ahead"); Outdated = link revision **lower** than upstream (link lags behind an updated item). Your definitions for both are fully inverted.

**3.2 The revision-bump consequence is wrong, as a consequence of 3.1.** You wrote "Incrementing a revision… voids existing coverage links — they become `Predated` defects." After the bump, a downstream `Covers:` entry still references the *older* upstream revision — which is **Outdated**, not Predated. The user guide's "Specification Item Revision" section says the bump "voids all existing links" without naming which status they flip to, but combined with the definitions in 3.1, that status is Outdated.

**3.3 `Status:` placement rule is truncated.** You wrote "appears before the description." The user guide's Keywords/Status entry says Status "has to occur before the `Description`, `Rationale` *or* `Comment`." Your version permits placing Status between Description and Rationale; the guide does not.

**3.4 "`Rationale:` / `Comment:` — at most one per item" is unwarranted.** The user guide states no cardinality limit for either keyword. Items in the guide's examples happen to use each once, but the primary source does not document a one-per-item rule. Claim should be softened to "conventionally used at most once" or removed.

**3.5 Forwarding is allowed *after* Needs/Covers/Depends/Tags sections, not "within" them.** The user guide's "Delegating Requirement Coverage" section explicitly lists positions: *after a title, after a Needs section, after a Depends section, after a Covers section, after a Tags section.* Your "within" wording is wrong — and the guide's whole point about forwards terminating the item means a forward cannot logically be "inside" a still-ongoing keyword block.

**3.6 "Silently terminates" understates a documented hazard.** The user guide explicitly flags the footgun: any `Needs:`/`Covers:`/etc. placed after a forward is silently dropped ("`Needs: impl,utest` ← this is now lost"). The guide also recommends collecting forwards in a separate titled section to avoid the trap. Your doc captures the termination fact but not the practical warning and mitigation, which is the reason the guide highlights the behavior in the first place.

**3.7 "Terminating specification item" definition is too narrow.** You wrote: "empty `Needs:` (no downstream types)." The user guide's "Terminating Specification Item" section says: "A specification item terminates a chain of items if it does not require coverage in any artifact type." Items with **no `Needs:` keyword at all** are equally terminating — and that's the common case (see the minimal `` `req~this-is-the-id~1` `` example). Your phrasing implies the author must explicitly write an empty Needs block, which is not required.

**3.8 "Tag Importer output defaults to revision 0" is not in the user guide** (unwarranted confidence). The user guide describes revision as "a positive integer number that can be started at zero but by convention usually is started at one" and shows an example with `~0` in a generated ID, but never explicitly states a Tag Importer default. Claim should be cited to a code/developer-doc source or removed.

**3.9 "`Tags:` — comma-separated list" is not explicitly documented.** The user guide's only keyword-level Tags example shows a single tag: `Tags: AuthenticationProvider`. Comma-separated format appears on the CLI `-t, --wanted-tags` flag but is not demonstrated for the spec-item keyword. The format is likely correct but not sourced to the primary reference.

**3.10 Compact-forward bullet character.** You show only `` - `dsn-->impl:req~bar~1` ``. The user guide's canonical example uses `*`. Any of `-`, `*`, `+` is accepted — so this is a presentation nit, not an error — but a reader reproducing the bullet style should know the guide favors `*`.

### What is correct (verified)
A lot, actually. The `type` = ASCII-letters-only rule ("no other characters are allowed"), the complete **name** regex (Unicode letter start; then Unicode letters, digits, `-`, `_`, `.`; no whitespace; **no consecutive dots** — all four clauses verbatim), the recommended artifact type list (feat/req/arch/dsn/impl/utest/itest/stest/uman/oman), **Status values = draft, proposed, approved** (complete, no `rejected`), Status affecting only the aspec XML report, the Needs two-forms-mutually-exclusive rule, Depends being XML-output-only, Covers being bullet-only with IDs including revision, the exact `<!-- oft:off -->` / `<!-- oft:on -->` tokens, both file extensions (`.md` and `.markdown` only), the two-dash arrow to avoid collisions, the canonical-vs-compact forward syntax (spaces-vs-no-spaces), forwards being ignored inside description/rationale/comment, the four incoming statuses (no "Covered Deep" exists), and the `aspec` report name with its stricter `approved`-required shallow-coverage check. The Java `openfasttrace-x.y.z.jar` naming is accurate.

### B. Gaps worth closing
The most important gap is terminological: the user guide classifies `Duplicate` as a **bidirectional link status**, not an "other defect" — if a practitioner reads your doc first and then tries to grep the guide for "Duplicate defect," they'll be mildly confused. Second: the console report uses a **`+type` form** (e.g., `+itest`) to indicate coverage of an *unrequested* artifact type, symmetric to your `-type` missing-coverage marker — your doc mentions only the minus form. Third: the format accepts **Setext-style (underlined) titles** (`=` for H1, `-` for H2) since OFT 3.8.0, which matters for teams using RST-compatible authoring. Fourth: `Description:` itself has a placement rule — "must occur before `Comment` or `Rationale`" — which your doc treats as simply optional. Fifth: the guide strongly recommends placing forwards in a **separate titled section** because of the termination-eats-subsequent-fields hazard flagged in 3.6.

---

## What to fix first

The ranked fix list, highest to lowest stakes: **(1)** swap Predated and Outdated in `oft-format.md` and fix the revision-bump consequence that follows from it; **(2)** fix the RFC 2119 §6 "should"-that-should-be-MUST in `rfc2119.md` and the `MAY` interoperability period; **(3)** add the two dropped "particular"s in the SHOULD / SHOULD NOT definitions; **(4)** attribute the uppercase and optional-use rules to RFC 8174 rather than leaving them implicitly sourced to RFC 2119; **(5)** reconcile `ears.md`'s "five patterns" and all-caps-keyword convention with Mavin's current six-pattern, sentence-case site, or add an explicit note that you are following the paper over the site. Everything else is either softening confident unsourced claims or closing a gap.