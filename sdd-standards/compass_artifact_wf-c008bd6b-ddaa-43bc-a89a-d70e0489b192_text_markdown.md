# Accuracy audit of rfc2119.md, ears.md, and oft-format.md

Your three documents are **directionally correct but carry material errors in each file**. The most serious are: an inverted modal in the SHOULD NOT definition (rfc2119.md), an attribution of a decomposition recommendation that the 2009 EARS paper does not make (ears.md), and an incomplete and partly wrong defect-type list plus a `rejected` status that OFT does not define (oft-format.md). Details below. Errors first, missing highlights second, per document.

---

## 1. RFC 2119 / RFC 8174

### Errors

**1.1. SHOULD NOT definition flips "should" to "must".**
Your doc: *"SHOULD NOT … the full implications **must** be understood and the case carefully weighed."*
RFC 2119 §4: *"the full implications **should** be understood and the case carefully weighed before implementing any behavior described with this label."*
You appear to have copied the §3 (SHOULD) wording into §4 (SHOULD NOT), which upgrades the epistemic force of the definition itself. Fix: use "should" in the SHOULD NOT gloss. Source: https://www.rfc-editor.org/rfc/rfc2119#section-4

**1.2. MAY definition drops half the interoperability rule and substitutes "authors" for "vendors/implementations".**
Your doc: *"An author may include it … another author may omit it, and interoperability with an implementation that omits it must still be possible."*
RFC 2119 §5 actually requires bidirectional interoperability — both (a) an implementation lacking the option must interoperate with one that has it, *and* (b) an implementation that has the option must interoperate with one that lacks it. The RFC also frames this around vendors and implementations, not document authors. Your one-directional, author-framed version is a category error. Source: https://www.rfc-editor.org/rfc/rfc2119#section-5

**1.3. Section 6 example is wrong; "dilutes the signal" is not in the RFC.**
Your doc: *"Requirements should be used only where actually required for interoperability or to limit harmful behavior (e.g., **data loss, security breach**). Over-use of MUST dilutes the signal."*
RFC 2119 §6's only concrete harm example is **"limiting retransmissions"** (the RFC even contains the typo "retransmisssions"). "Data loss, security breach" is your gloss presented as canonical. And the "dilutes the signal" line is nowhere in RFC 2119 — plausible editorial advice, but not sourced. The RFC also uses "interoperation" (not "interoperability") in the binding sentence. Source: https://www.rfc-editor.org/rfc/rfc2119#section-6

**1.4. "Exact synonyms / interchangeable / authorial preference" overstates the RFC.**
RFC 2119 §1–2 says the terms "**mean**" the same thing for interpretive purposes. It never says "exact synonyms," never says "interchangeable," and makes no claim about authorial choice. There is a longstanding community distinction (rooted in RFC 2026) between SHALL (used for protocol conformance) and MUST/REQUIRED (used more broadly) that some specs honor in practice. Your framing collapses a real subtlety. Safer wording: "RFC 2119 defines MUST, REQUIRED, and SHALL to carry the same meaning in interpretation." Source: https://www.rfc-editor.org/rfc/rfc2119#section-1

**1.5. Author affiliation is "Harvard University", not "IETF".**
Your doc lists "Author: S. Bradner, IETF, March 1997." Bradner's listed affiliation on the RFC is **Harvard University**; the IETF is the publisher/stream. Minor but it's on the front matter. Source: https://www.rfc-editor.org/rfc/rfc2119

**1.6. "RFC 2119 … says nothing about how a requirement is phrased" — mild overclaim.**
The RFC doesn't declare phrasing out of scope; it simply doesn't cover it. And §6 *does* lightly constrain content ("they must not be used to try to impose a particular method on implementors where the method is not required for interoperability"), which brushes against phrasing. Defensible summary, but don't present it as something the RFC itself asserts.

### Missing highlights

- **RFC 8174's formal title** is *"Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"* (Leiba, Huawei, May 2017). Your doc omits it.
- **RFC 8174 adds "NOT RECOMMENDED" to the boilerplate enumeration** (RFC 2119 defined it in §4 but omitted it from the boilerplate list).
- **The exact RFC 8174 replacement boilerplate** that conforming documents should embed is worth quoting verbatim: *"The key words 'MUST', 'MUST NOT', 'REQUIRED', 'SHALL', 'SHALL NOT', 'SHOULD', 'SHOULD NOT', 'RECOMMENDED', 'NOT RECOMMENDED', 'MAY', and 'OPTIONAL' in this document are to be interpreted as described in BCP 14 [RFC2119] [RFC8174] **when, and only when, they appear in all capitals, as shown here.**"*
- **RFC 8174 also makes key-word use optional**, not just case-sensitive: *"normative text does not require the use of these key words."* Your paraphrase only captures the case-sensitivity half.
- **BCP 14 is now jointly RFC 2119 + RFC 8174**, and proper citation is "BCP 14 [RFC2119] [RFC8174]".
- **The sentence "Note that the force of these words is modified by the requirement level of the document in which they are used"** (right after RFC 2119's boilerplate) is load-bearing — a MUST in an Informational RFC differs in force from a MUST in a Standards Track RFC.
- **RFC 2119 §7 (Security Considerations)** directs authors to elaborate the security implications of non-compliance with each MUST/SHOULD — useful operational guidance you omit.
- **§6 also forbids using imperatives to impose particular methods on implementors where not required for interoperability** — an operational rule stronger than "use sparingly."

---

## 2. EARS (RE'09 + Big Ears RE'10)

The 2009 paper was available as an IEEE-stamped PDF via an academic mirror; Big Ears RE'10 is paywalled and was verified only via the abstract plus fragments.

### Errors

**2.1. "EARS templates use a modal verb slot (canonically 'shall') that any RFC 2119 word may occupy without altering the template's structural validity" — not in the paper.**
The 2009 paper hard-codes `shall` in every generic template and every example. It does not mention RFC 2119, does not discuss modal substitution, and does not state that the modal slot is fungible. Your bridge between RFC 2119 and EARS is your own framing. It's a reasonable design decision for your system, but don't attribute it to EARS. Source: RE'09 §4.

**2.2. "The original paper recommends decomposing them into multiple simpler requirements when practical" — the 2009 paper does NOT say this.**
RE'09 §4.7 ("Complex requirement syntax") treats complex requirements entirely positively: *"The keywords can be built into more complex expressions to specify richer system behaviours."* It does not call them harder to verify, harder to read, or discouraged, and it does not recommend decomposition. The paper does mention decomposing compound *source-text* into atomic requirements, but that is input pre-processing, not a critique of EARS complex form. This is a **material misattribution** — remove or re-source.

**2.3. "harder to verify" is your characterization, not the paper's.**
Same section as 2.2. The paper does not use that phrase about complex EARS requirements.

**2.4. Unwanted-behavior template is simplified away from the paper.**
Your doc: `"If <condition>, then the <system> shall <action>."`
RE'09 §4.4: `IF <optional preconditions> <trigger>, THEN the <system name> shall <system response>.` The paper explicitly distinguishes **optional preconditions** from the **trigger**; you collapsed them into a single `<condition>`. The `then` placement is correct (this is the most common point of confusion in secondary writeups, and you got it right).

**2.5. State-driven omits the sanctioned alternative keyword "During".**
RE'09 §4.5: *"To make requirements easier to read, the keyword **During** can be used instead of While for state-driven requirements."* Your doc lists only "While".

**2.6. "Jet-engine control software" is a loose paraphrase.**
The RE'09 paper says Rolls-Royce Control Systems develops **Full Authority Digital Engine Controllers (FADECs) for civil gas turbine engines** and that the case study was CS-E 50. "Jet engine" is informally accurate (Mavin himself uses it now) but drops precision. Not an error, but worth noting.

**2.7. "EARS does NOT define: obligation strength, identity, rationale, metadata" is your framing, not the paper's.**
The paper does say it is *"principally concerned with requirements syntax"* and that semantics improvements were out of scope, which gets you most of the way there. But the enumeration of what EARS *doesn't* cover (obligation strength, identity, rationale, metadata) is your bulleted inference. Present it as such.

### Missing highlights

**From the 2009 paper:**
- **The unifying generic template** `<optional preconditions> <optional trigger> the <system name> shall <system response>` — all five patterns are specializations of this. The ordering (state → event → subject) is *"based on temporal logic"* per §4.1. Your doc presents the five patterns as five separate forms without this structure.
- **The eight problems EARS targets**: ambiguity, vagueness, complexity, omission, duplication, wordiness, inappropriate implementation detail, untestability. This is the paper's motivation.
- **Scope limit**: EARS is targeted at **high-level stakeholder requirements**, and the paper explicitly disclaims universal applicability at all decomposition levels.
- **Design rationale for Unwanted**: its syntax is *"derived from event-driven requirements"*, and a dedicated pattern exists because *"unwanted behaviour is a major source of omissions in early requirements."*
- **§7 future-work acknowledgment** that unwanted *states* (not just unwanted *events*) may need an additional template — the paper itself signals the five-pattern set may be incomplete.
- **Capitalization convention**: the paper capitalizes keywords (WHEN, WHILE, WHERE, IF…THEN) in generic templates.

**From Big Ears (RE'10) — what's new or refined:**
- **Lessons Learned section** with applied guidance for authoring EARS in practice.
- **Wider empirical validation**: back-to-back before/after experiments on multiple requirement sets.
- **"Hidden functions"** — internal, user-imperceptible behaviors, addressed as a new category.
- **"Design Active" vs "Design Passive" responses** — informal classification of response types (e.g., passive EMI response).
- **Recommended combinations** — explicit guidance on which pattern combinations form sensible complex requirements (partial remediation of the 2009 paper's silence on this).
- **Defense of If-Then** — 2010 paper explicitly engages the criticism that Unwanted is behaviorally identical to Event-driven, and defends keeping them distinct.
- **Templates were refined and known limitations addressed** (per abstract) — worth pulling the full text if available.

**From Mavin's later canonical materials** (not required, but the ecosystem):
- **Complex is often listed as a sixth named pattern** on alistairmavin.com/ears/ and in Terzakis's Intel tutorial, with its own template `While <precondition(s)>, When <trigger>, the <system name> shall <system response>`. If your system treats Complex as first-class, cite the author's current page rather than RE'09.

---

## 3. OpenFastTrace

### Errors

**3.1. Status value `rejected` is not defined.**
Your doc: *"Status: draft/proposed/approved/rejected."*
User guide (Keywords → Status): *"The `Status` keyword takes a single value from `draft`, `proposed`, `approved` to set the status of the item."* Only **three** values are documented. Drop `rejected`. Source: https://github.com/itsallcode/openfasttrace/blob/main/doc/user_guide.md#status

**3.2. "Draft participates in coverage identically to approved" — wrong for the aspec (XML) report.**
User guide (XML Tracing Report, `<shallowCoverageStatus>`): *"`COVERED` if for all needed requirement types another valid requirement covers the requirement. **Valid in this case also means that the covering requirement has status `approved`.**"* So for aspec output, a `draft` item does **not** satisfy shallow coverage. The user guide separately confirms Status has no effect on HTML/plaintext output. Your blanket statement is correct only for the default reports.

**3.3. Defect-type list is incomplete and partly wrong.**
Your doc lists four: uncovered need, unresolved cover, revision mismatch, orphan.
The user guide's actual status vocabulary is much richer. Outgoing link statuses: **Covers** (ok), **Predated**, **Outdated**, **Ambiguous**, **Unwanted**, **Orphaned**. Incoming: **Covered Shallow** (ok), **Covered Unwanted**, **Covered Predated**, **Covered Outdated**. Plus **Duplicate** (two items with same ID defined).

Specific issues:
- You collapse **Predated** (pointing at a newer revision than exists) and **Outdated** (pointing at an older revision than the current one) into one "revision mismatch". These are opposite defects with different causes and remediations.
- "Uncovered need" / "unresolved cover" are not user-guide terms — missing coverage is surfaced in the summary with a minus-prefixed artifact type (e.g. `(-impl, utest)`), not as a named status.
- You omit **Unwanted / Covered Unwanted** (coverage the target did not request), **Ambiguous** (links resolve to multiple items with the same ID), and **Duplicate** entirely.

**3.4. Revision: zero is allowed.**
Your doc: *"revision: positive integer, conventionally starts at 1."*
User guide: *"The revision number … is a positive integer number that **can be started at zero** but by convention usually is started at one."* (The guide's own wording is internally sloppy.) Revision `0` is used in practice — auto-generated implementation tags via the Tag Importer default to revision `0` (`impl~…~0`).

**3.5. `Needs` also supports a bullet-list form.**
Your doc: *"Needs: comma-separated list."*
User guide: *"`Needs` comes in two flavors: as one-liner or as list … you cannot mix the two styles in one specification item."* Both `Needs: impl, utest, itest` and a bullet form are legal.

**3.6. `.markdown` is also recognized, not just `.md`.**
User guide (Input Format Support → Markdown): *"accepts markdown files with the extensions `.md` and `.markdown`."* Your claim that "every `.md` file" is scanned omits the second extension. The guide also lists ReStructured Text (`.rst`) as a separate importer with its own exclusion markers (`.. oft:off` / `.. oft:on`), which is scoped out of your doc but worth noting.

**3.7. Artifact-type list is recommended, not canonical.**
Your doc presents the list as if it were fixed. User guide (Specification Item Artifact Type): *"**While not enforced by OFT** the following strings are well established … How many types you introduce, how you name and stack them is up to you."* Users are free to define their own. The ten you list match the guide's recommended set, but the framing needs the "not enforced" caveat.

**3.8. Horizontal-rule terminator is not documented as such.**
Your doc: *"Item ends at … a horizontal rule (---) …"*
The user guide does not document `---` as an item terminator. It does say **a forward terminates the preceding item**, and the changelog notes that items inside fenced code blocks are ignored. Your `---` claim is an inference beyond what the docs say — flag as "user's inference" rather than primary-sourced fact, especially since you told the auditor to trust only the docs.

**3.9. Forwarding syntax details are thinner than the guide.**
Your doc: `arch --> dsn : req~auth.login~1` — correct primary form. But the guide also documents a compact backtick-wrapped bullet form `` `dsn-->impl:req~bar~1` `` (no spaces), specifies that the arrow uses two dashes *"to reduce the chance for parsing collisions,"* enumerates the exact allowed placements (after a title, `Needs`, `Depends`, `Covers`, or `Tags` section), and warns that a forward inside a description/comment/rationale block is ignored. A forward also **silently terminates the preceding item**, which is a common source of bugs.

**3.10. Revision-bump wording overstates breakage.**
Your doc: *"a revision bump immediately breaks all downstream links."*
User guide language is softer and more precise: revision *"is intended to obsolete existing coverage links in case the content of a specification item semantically changed"* and *"Incrementing the revision voids all existing links to this item so that authors linking to the item know they have to check for changes."* The guide also **warns against bumping for cosmetic edits** (added a missing period, etc.). Operationally, stale links become `Outdated` defects (still visible, flagged for remediation) — they don't disappear. The distinction matters for remediation workflows.

**3.11. Backtick wrapping for IDs — convention, not stated requirement.**
Every user-guide example wraps IDs in backticks, but the docs do not explicitly mandate it. Treat as strong convention, not hard rule.

### Missing highlights

- **Setext-style headings** (title underlined with `=` or `-`) have been accepted since 3.8.0 — relevant if you mix RST-style headings.
- **Fenced code blocks exclude items** (changelog #480). Prevents accidental item creation when documenting OFT itself.
- **Tag Importer format** for source-code traceability is distinct from the Markdown format: `[covered-artifact-type->specification-object-id]` and extended forms `[type~~revision->id]` / `[type~name~revision->id]`. This is why `revision = 0` exists in practice.
- **`approved`-only shallow coverage in aspec** (repeat of Error 3.2, but worth its own mention because it materially changes tracing verdicts).
- **`-a` / `-i` / `-t` filters** at import time change which items are considered. `_` as the first tag in `-t` is a sentinel meaning "also include untagged items."
- **`<dependsOnSpecObject>` in aspec XML** lives outside `<covering>`. Relevant if you build downstream tooling on the XML.
- **"Terminating specification item"** is a formal concept in the guide — an item with no needed types is a leaf and never appears as an uncovered defect.
- **EB Markdown variant** is supported for backward compatibility (Elektrobit-originated). Not relevant for new docs, but you'll see references in the repo.

---

## Conclusion

Across the three files, your recurring pattern is **semantic drift**: confident, tidy summaries that paraphrase primary sources slightly beyond what they actually say. The RFC 2119 doc flips a modal and invents a harm example. The EARS doc attributes a decomposition recommendation the 2009 paper does not make, and bridges EARS↔RFC 2119 with a claim the paper does not support. The OFT doc compresses ten-plus defect types into four, adds a status value the tool does not define, and overstates revision-bump consequences.

**Priority fixes, in order:**
1. Fix the SHOULD NOT wording in rfc2119.md (§4 uses "should", not "must").
2. Remove or re-source the "decomposing complex requirements" claim in ears.md.
3. Replace the four-defect list in oft-format.md with the full status vocabulary, and separate Predated from Outdated.
4. Drop `rejected` from OFT status values and add the aspec-only "approved satisfies shallow coverage" caveat.
5. Reframe the RFC 2119 ↔ EARS bridge as your system's design decision, not as something either standard asserts.

Secondary upgrade opportunities: add the unified EARS generic template, add `During` as an alternative state-driven keyword, add RFC 8174's exact boilerplate and its optionality clause, and add the aspec/tag-importer distinctions and `.markdown` extension support in OFT.