---
type: General-Sheet
title: Testing Family Rule Audit
description: The rule audit over the testing/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Testing Family Rule Audit

The family holds twenty-four rules, all in
[Testing Conventions](/standards/testing/conventions.md). One
reclassification is proposed, deterministic to stochastic:
`testing.the-mocking-library` cannot be decided without first judging
which doubles in a suite are mocks, and this suite hand-rolls every one
of them. No rule is proposed for the other direction. Four rules break:
`testing.conftest-hierarchy`, whose root `tests/conftest.py` holds one
fixture no test uses and one every user of which sits a directory lower;
`testing.fixtures-for-setup-and-teardown`, which nine test modules
sidestep with a module-local `make_repo` helper called from the test
body; `testing.one-fake-per-interface`, where the one `runner` port
carries six separate doubles; and `testing.the-mocking-library`, whose
`unittest.mock` appears nowhere in the suite. One rule is weakly
checked, `testing.access-only-public-names`: testing-lint opens only
files named `test_*.py`, so the `conftest.py` and fake modules the
population names go unread, and a rebound local name hides a private
reach. Two rules are checked in full, `testing.mirror-source-structure`
and `testing.no-logic-in-tests`; the other twenty-one verifier rows are
null. Three rules are low value: `testing.pytest`, which
`build.pyprojecttoml` already pins; `testing.test-file-naming`, which is
true by the population's own wording; and `testing.the-mocking-library`.

| id | rule | kind | proposed | check | state | overlap | value | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `testing.pytest` | "A governed repo's Python test suite runs on pytest." | deterministic | deterministic | none | holds | `build.pyprojecttoml` | low | Test: `pyproject.toml` carries `[tool.pytest.ini_options]` and a `pytest` floor in `[dependency-groups] dev`. Both present. `build.pyprojecttoml` pins `tool.pytest.ini_options.testpaths` and the canonical `pytest>=9.0` floor, so it subsumes this. |
| `testing.test-file-naming` | "Every test file in the suite is named `test_*.py`." | deterministic | deterministic | none | holds | none | low | True by construction: the `population` defines a test file as a `test_*.py` file, so no member can falsify it. A script could not find the counterexample, because the counterexample is not a member. |
| `testing.mirror-source-structure` | "A `test_*.py` file under `tests/` whose name, with the `test_` prefix removed, is the file name of a module under `src/` other than an `__init__.py` sits at that module's mirror: `tests/`, then the module's directory path below `src/`, then the file name with `test_` prefixed, so that `src/auth/login.py` is tested at `tests/auth/test_login.py`; or at that same path beneath one of the two scope directories `unit` and `integration`, as `tests/unit/auth/test_login.py`." | deterministic | deterministic | full | holds | none | high | testing-lint's `check_mirror_layout` builds the same mirror set, `unit` and `integration` included, and accepts any one where a stem names several modules. I recomputed it over all 427 tracked files: no violation. |
| `testing.conftest-hierarchy` | "A fixture lives in the `conftest.py` of the narrowest directory whose tests use it." | deterministic | deterministic | none | breaks | none | high | `tests/conftest.py:94` defines `make_repo`, which no test requests; `tests/conftest.py:67` defines `ambient_git_dir`, whose five users all sit under `tests/dev_playbook/`. See the escalation. |
| `testing.arrange-act-assert` | "The body of a `test_*` function sets up its conditions, then performs the one action under test, then verifies the result, in that order and with no setup after the action." | stochastic | stochastic | none | holds | none | high | "Sets up its conditions" cannot be told from "performs the action" without reading intent. Sampled six modules, among them `tests/dev_playbook/test_findings.py` and `tests/test_transcript_export_client.py`: no setup after the action. |
| `testing.one-concept-per-test` | "Each test verifies one behavior or scenario, and every assertion in it verifies a facet of that one behavior." | stochastic | stochastic | none | holds | none | high | Needs judgment on what one behavior is. Sampled as above. `test_session_list_builds_argv_and_returns_the_session_rows` in `tests/test_transcript_export_client.py:57` is the closest call: two facets of one call's contract. |
| `testing.no-logic-in-tests` | "The body of a `test_*` function holds no `if`/`else` statement and no `try`/`except` statement, except inside a function or a class defined within that body." | deterministic | deterministic | full | holds | none | high | testing-lint's `check_no_logic` flags `ast.If` and `ast.Try` under a `test_*` function, skipping nested `FunctionDef`, `AsyncFunctionDef` and `ClassDef`. The one `try` in the suite, `tests/dev_playbook/cloa_viewer/test_cli.py:102`, sits in a module helper. |
| `testing.expected-values-come-from-outside-the-code` | "A test's expected value is a known-good literal, a worked example, or the spec, and never a value the test recomputes the way the code under test computes it." | stochastic | stochastic | none | holds | none | high | Deciding "recomputes the way the code does" needs the code's shape held against the test's. Sampled expectations are literals, e.g. `tests/dev_playbook/test_findings.py:11` asserts the exact finding line. |
| `testing.access-only-public-names` | "A test reaches a module that is not itself a test module only through identifiers that do not begin with an underscore: not an imported name, not a segment of an imported module path, and not an attribute reached through an imported name." | deterministic | deterministic | weak | holds | none | high | testing-lint reads only `test_*.py`, so `tests/conftest.py`, `tests/transcript_fakes.py` and `tests/cloa_viewer_fixtures.py` are unread; a rebound local name and `from . import _x` also escape. All three files are clean today. |
| `testing.assert-on-observable-outputs` | "A test's assertions are on observable outputs: return values, state changes such as a record stored or a file written, and raised exceptions." | stochastic | stochastic | none | holds | none | high | "Observable" is the judgment: a private attribute is observable to Python. Sampled assertions are on exit codes, stdout, return values and raised exceptions. |
| `testing.assert-on-outcomes-not-call-sequences` | "Where a test uses a mock, its assertion is the minimum that verifies the contract — "the record is in the store" rather than "insert was called once with these arguments" — unless a call count, an argument shape, or a call ordering is itself the contract." | stochastic | stochastic | none | holds | `testing.assert-on-observable-outputs` | high | `tests/test_transcript_export_client.py:64` asserts an exact argv list, but argument building is that module's stated contract, so the exception applies. assert-on-observable-outputs is the broader rule; this adds the minimality bar for mocks. |
| `testing.name-by-capability-not-mechanism` | "A test's name states the capability under test and survives an implementation swap: `test_request_includes_trace_id`, not `test_structlog_processor_adds_trace_id`." | stochastic | stochastic | none | holds | none | high | "Survives an implementation swap" needs to know which names are the implementation. Sampled names read as capabilities, e.g. `test_import_of_private_name_from_non_test_module_is_flagged`. |
| `testing.replace-dont-layer` | "Once a module is covered through its own interface, the unit tests on the smaller pieces beneath it are deleted rather than kept." | stochastic | stochastic | none | unknown | none | high | Settling it needs a coverage map over about 1,100 tests. One candidate I could not resolve: `tests/dev_playbook/test_findings.py` covers `findings.render` directly while every lint suite also asserts on rendered finding lines. |
| `testing.no-test-of-a-non-deterministic-decision` | "No test asserts on the output of a non-deterministic component such as an LLM call, a network request, or a source of randomness." | stochastic | stochastic | none | holds | `testing.mocks-at-boundaries-only` | high | Which component is non-deterministic is the judgment. No LLM call, no outbound network, no `random`. `tests/dev_playbook/cloa_viewer/test_cli.py` drives a localhost server the test itself starts. mocks-at-boundaries-only names the same class as its third boundary. |
| `testing.the-lightest-double` | "A dependency is doubled with the lightest thing that verifies the behavior under test — a real object, then a fake, then a mock — and a real implementation that is cheap and deterministic is used as it is." | stochastic | stochastic | none | holds | none | high | "Cheap and deterministic" is the judgment. The suite uses real git repos under `tmp_path`, real subprocess runs and a real in-process server, and doubles only the `agentsview` subprocess. |
| `testing.double-at-the-port` | "Where the code under test reaches a dependency over the network, the test doubles the port that code defines for the dependency rather than the network client itself." | stochastic | stochastic | none | holds | none | high | Recognizing a port needs judgment. `src/dev_playbook/transcript_export/client.py:60` defines the seam `runner: Callable = subprocess.run`, and every double sits there, not on `subprocess` itself. |
| `testing.fakes-for-stateful-dependencies` | "A dependency whose state or logic the tests exercise, and a dependency several tests share, is faked rather than mocked." | stochastic | stochastic | none | holds | `testing.the-lightest-double` | high | `tests/transcript_fakes.py:128` `fake_daemon` holds an in-memory session map and real paging logic, shared by three modules. the-lightest-double states the same ladder; this is its middle rung. |
| `testing.one-fake-per-interface` | "The suite holds one fake for an interface, and every test that doubles that interface uses it." | stochastic | stochastic | none | breaks | none | high | The one `runner` port carries six doubles: `fake_daemon`, `list_runner`, `search_runner`, `refused_runner`, `boom_runner`, `recording_runner`. See the escalation. |
| `testing.fakes-live-in-the-test-tree` | "A fake lives under `tests/`, in `tests/fakes.py` or beside the tests that use it." | stochastic | stochastic | none | holds | none | high | Identifying a fake is the judgment. `tests/transcript_fakes.py` sits beside `tests/test_transcript_export_*.py`. `tests/cloa_viewer_fixtures.py` sits a directory above its users but builds a fixture checkout rather than doubling an interface. |
| `testing.fakes-implement-only-what-callers-use` | "A fake implements only the methods its callers call." | stochastic | stochastic | none | holds | none | high | `fake_daemon` serves `session get` and `session messages` and raises `AssertionError` on anything else; `session list` and `session search`, which its callers never reach, are absent. |
| `testing.mocks-at-boundaries-only` | "A mock stands at a boundary and at that boundary's entry point, and deeper in the call chain a fake takes its place." | stochastic | stochastic | none | holds | `testing.the-lightest-double` | high | `recording_runner` stands at the `runner` seam, which is the subprocess boundary's entry point. the-lightest-double states the same ladder; this is its top rung. |
| `testing.the-mocking-library` | "A mock in the suite is built with `unittest.mock`." | deterministic | stochastic | none | breaks | none | low | `unittest.mock` is imported nowhere in the suite, yet `tests/test_transcript_export_client.py:34` hand-rolls a recording double. Deciding the rule first needs a judgment on which doubles are mocks. See the escalation. |
| `testing.fixtures-for-setup-and-teardown` | "Construction and cleanup go through pytest fixtures rather than ad-hoc setup code in a test body." | stochastic | stochastic | none | breaks | `testing.conftest-hierarchy` | high | Nine test modules define a module-local `make_repo` function and call it from the test body, e.g. `tests/test_repo_lint.py:37`. See the escalation. conftest-hierarchy presupposes this rule by saying where a fixture lives. |
| `testing.narrowest-fixture-scope` | "A fixture takes the narrowest scope that works: function, the default, then class, then module, then session." | stochastic | stochastic | none | holds | none | high | "That works" is the judgment: no script can tell whether a wider scope would still pass. No `scope=` appears anywhere in the suite, so every fixture is function-scoped. |

## Escalations

### `testing.conftest-hierarchy` — "A fixture lives in the `conftest.py` of the narrowest directory whose tests use it."

Two breaks, and one reading question behind them.

The plain break is `ambient_git_dir`, defined at `tests/conftest.py:67`.
Its five users are `tests/dev_playbook/test_gitrepo.py:16`,
`tests/dev_playbook/test_pyast.py:12`, `tests/dev_playbook/test_md.py:302`,
`tests/dev_playbook/test_verifier_table.py:395` and
`tests/dev_playbook/test_workspace_lint.py:1605`. Every one sits under
`tests/dev_playbook/`, so the narrowest directory whose tests use the
fixture is `tests/dev_playbook/`, which carries no `conftest.py` at all.
The fixture sits one level too high.

The second break is `make_repo`, defined at `tests/conftest.py:94`. No
test requests it: the nine modules that use a name spelled `make_repo`
each define their own module-level function of that name and call it
directly — `tests/test_harness_files_lint.py:60`,
`tests/test_python_lint.py:23`, `tests/test_repo_lint.py:37`,
`tests/dev_playbook/test_decisions_lint.py:28`,
`tests/dev_playbook/test_testing_lint.py:25`,
`tests/dev_playbook/test_loop_lint.py:63`,
`tests/dev_playbook/test_verifier_table.py:21`,
`tests/dev_playbook/test_prose_lint.py:25` and
`tests/dev_playbook/test_standards_lint.py:19`. A fixture with no users
has no narrowest directory, so the predicate has nothing true to say
about it.

The reading question: about thirty fixtures live in the test modules
that use them, not in any `conftest.py` — `tests/test_ref_lint.py:63`,
`tests/dev_playbook/cloa_viewer/test_server.py:19` and twelve more in
`tests/dev_playbook/cloa_viewer/test_cli.py` among them. A module is not
a directory, so a literal reading makes every one of them a break. The
[Test Design Explanation](/standards/testing/explanation.md) reads the
other way: it speaks of each directory level carrying its own
`conftest.py` so that a domain-specific fixture stays with the tests of
its domain, which is about hoisting, not about banning a module-local
fixture.

**Proposal.** Rewrite, then make one small repo change. Rewrite the
predicate to state the anti-hoisting rule the explanation describes and
the repo follows: "A fixture more than one test file uses lives in the
`conftest.py` of the narrowest directory whose tests use it; a fixture
one test file uses lives in that file." Under that sentence the thirty
module-local fixtures are correct and `ambient_git_dir` is still wrong,
so also move `ambient_git_dir` from `tests/conftest.py` into a new
`tests/dev_playbook/conftest.py` and delete the unused `make_repo`
fixture from `tests/conftest.py`. I recommend the repo change here only
because the root `conftest.py` plainly means to hold what the whole
suite shares, and nine modules writing their own `make_repo` rather than
requesting the one in `conftest.py` is evidence that the hoisted copies
are an oversight, not a decision.

### `testing.fixtures-for-setup-and-teardown` — "Construction and cleanup go through pytest fixtures rather than ad-hoc setup code in a test body."

The suite's dominant construction pattern is a module-level plain
function called from inside the test body. `tests/test_repo_lint.py:37`
defines `make_repo(tmp_path, files, name, executable, symlinks)`, which
writes files, chmods, symlinks and runs `git init` and `git add -A`;
`tests/test_repo_lint.py:76` and `:95` define the further builders
`python_files` and `scripts_only_files`. Each of the fifty-nine tests in
that module calls them in its own body. Eight more modules do the same,
listed in the escalation above. `tests/dev_playbook/test_testing_lint.py`
adds a second such helper, `run(repo)` at line 16, which performs the
subprocess call.

The repo went this way on purpose: `tests/conftest.py:94` already offers
`make_repo` as a fixture and not one test takes it. The predicate as
written calls the whole pattern ad-hoc setup in a test body, so the
suite is false of it.

**Proposal.** Rewrite the predicate to the narrower thing the repo
actually holds itself to — teardown, and only teardown, must be a
fixture: "Cleanup that must run after a test goes through a pytest
fixture rather than code in a test body; construction may go through a
fixture or a factory helper the test calls." Rewriting rather than
changing the repo is right here because nine modules and roughly two
hundred tests follow the factory-helper pattern deliberately, and
`pytest`'s `tmp_path` fixture already handles the cleanup the rule
exists to guarantee.

### `testing.one-fake-per-interface` — "The suite holds one fake for an interface, and every test that doubles that interface uses it."

One interface, the `runner` callable that
`src/dev_playbook/transcript_export/client.py:60` accepts in place of
`subprocess.run`, carries six separate doubles:

- `fake_daemon`, `tests/transcript_fakes.py:128` — serves `session get`
  and `session messages` from an in-memory map, with real paging logic.
- `list_runner`, `tests/test_transcript_export.py:22` — serves canned
  `session list` pages.
- `search_runner`, `tests/test_transcript_export.py:36` — serves canned
  `session search` matches.
- `refused_runner`, `tests/test_transcript_export.py:52`.
- `boom_runner`, `tests/test_transcript_export.py:59`.
- `recording_runner`, `tests/test_transcript_export_client.py:34` —
  records argv and replays a queue of canned results.

`refused_runner` and `boom_runner` model failure modes and
`recording_runner` records interactions, so by the family's own
vocabulary those three are mocks rather than fakes. That still leaves
three fakes of one interface: `fake_daemon`, `list_runner` and
`search_runner`. The predicate says one.

**Proposal.** Change the repo: fold `list_runner` and `search_runner`
into `fake_daemon` in `tests/transcript_fakes.py` so the one fake
answers all four `session` subcommands, and update the callers in
`tests/test_transcript_export.py`. I recommend the repo change because
the three are the same kind of thing — a canned-response `agentsview`
daemon — and `fake_daemon`'s docstring already presents itself as the
suite's fake daemon; the split looks like two modules growing their own
copy rather than a decision to keep them apart. The mocks stay where
they are, since `testing.mocks-at-boundaries-only` admits them.

### `testing.the-mocking-library` — "A mock in the suite is built with `unittest.mock`."

`unittest.mock` is imported by no file in the suite: a grep for
`unittest.mock`, `MagicMock`, `patch(` and `mocker` across `tests/` and
`working-docs/software-factory/tests/` returns nothing. The suite does
hold mocks by the family's own definition, though.
`tests/test_transcript_export_client.py:34` defines `recording_runner`,
which appends each `args` list to a caller-supplied `calls` list and
pops a canned result off a queue; twenty-odd tests then assert on
`calls`, for instance the exact argv list at line 64 and the call count
at line 110. A double whose recorded interactions are the assertion is a
mock, not a fake. `refused_runner` and `boom_runner` at
`tests/test_transcript_export.py:52` and `:59` are the same shape.

The rule is also misclassified. Its trailer says deterministic, but a
script cannot apply the predicate without first deciding which of the
suite's doubles are mocks, and the family leaves that to the reader —
`recording_runner`'s own docstring calls itself a fake. That judgment is
the whole of the rule, so the kind is stochastic as the predicate stands.

**Proposal.** Rewrite the predicate to the deterministic residue, which
is the thing worth binding: "No test module imports a mocking library
other than `unittest.mock`." That sentence is true of the repo today, a
script decides it by reading import statements, and it keeps the one
choice the rule exists to make, which is that a repo does not add
`pytest-mock` or another mocking dependency. Delete is the alternative I
would accept, since the rule's value is low either way.

### `testing.access-only-public-names` — "A test reaches a module that is not itself a test module only through identifiers that do not begin with an underscore: not an imported name, not a segment of an imported module path, and not an attribute reached through an imported name."

The predicate binds "a test", and the population names `conftest.py`
and the fake modules as members of the suite. `testing_lint.py:342`
opens only a file whose name starts with `test_` and ends in `.py`, so
`tests/conftest.py`, `tests/transcript_fakes.py` and
`tests/cloa_viewer_fixtures.py` are never read. Inside a read file, a
name rebound locally (`x = mod._private; x()`) and a relative
`from . import _x` also escape the walk. All three unread files are
clean today, so the rule holds; the check is weak, not wrong.

## Detectors

**`scripts/testing-lint`** — a thin shim that puts the checkout's `src/`
on `sys.path` and calls `dev_playbook.testing_lint.main`. It is the only
check any rule in this family names, and it decides three of the
twenty-four: `testing.access-only-public-names`,
`testing.mirror-source-structure` and `testing.no-logic-in-tests`. The
boundary table runs it at `commit`, `push` and `ci`.

**`src/dev_playbook/testing_lint.py`** — the detector itself. It walks
the repo's Python files once and, for each file whose name begins with
`test_` and ends in `.py` and whose parent directories are not caches,
runs three checks. `check_mirror_layout` compares a test file under the
top-level `tests/` tree against the mirror set built from every
non-`__init__` module under `src/`, flat and under the fixed scopes
`unit` and `integration`, and emits one file-level finding with no line
number. `check_no_private_access` walks the AST, tracking imports and
rebindings, and flags a private module segment in an import, a private
name imported from a non-test module, and a private attribute reached
through a non-test import; a module path segment equal to `tests` or
`conftest`, or beginning with `test_`, marks a module as a test module
and exempts it. `check_no_logic` flags `ast.If` and `ast.Try` under a
`test_*` function, not descending into a nested function or class.

**`src/dev_playbook/pyast.py`** — the shared discovery and parse layer
testing-lint stands on. `find_python_files` lists candidates through
`git ls-files --cached --others --exclude-standard` under a scrubbed
environment, so discovery is gitignore-aware and worktree-scoped, and
`parse` returns `None` for a file that cannot be read or parsed, which
makes a syntactically broken test file invisible to the two AST rules.
