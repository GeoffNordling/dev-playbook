// The booby-trap test for Sandcastle itself: does run() run git on the host
// in the work copy, where anything the agent planted in the copy's .git fires?
// Call 1, a stand-in agent (a shell script, no tokens), commits and then
// plants the triggers of tests/dev_playbook/test_front_clone_traps.py; call 2
// is an ordinary second iteration on the same copy. Each trigger touches a
// marker in a folder that exists only on the host, so a marker is a trap that
// fired on the host. A control then runs `git status` on the host to prove
// the traps are live.
// Run setup.sh on the lab first.
// Usage: node traps.mjs <lab directory>
import { run } from "@ai-hero/sandcastle";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdirSync, readdirSync, rmSync } from "node:fs";
import { join } from "node:path";
import { relocated } from "./relocated.mjs";

const E = process.argv[2];
if (!E) throw new Error("usage: node traps.mjs <lab directory>");
const RIG = import.meta.dirname;
const WT = join(RIG, "../../../..");
const REAL = `${E}/real/mission-control`;
const COPY = `${E}/lap/traps/mission-control`;
const MARK = `${E}/markers`;
const HOME = "/home/agent";
const REPO = `${HOME}/assignment/mission-control`;

const HOOKS = [
  "applypatch-msg", "pre-applypatch", "post-applypatch", "pre-commit", "pre-merge-commit",
  "prepare-commit-msg", "commit-msg", "post-commit", "pre-rebase", "post-checkout", "post-merge",
  "pre-push", "pre-receive", "update", "proc-receive", "post-receive", "post-update",
  "reference-transaction", "push-to-checkout", "pre-auto-gc", "post-rewrite", "sendemail-validate",
  "fsmonitor-watchman", "p4-changelist", "p4-prepare-changelist", "p4-post-changelist",
  "p4-pre-submit", "post-index-change",
];

const standIn = {
  name: "stand-in",
  env: {},
  captureSessions: false,
  buildPrintCommand: ({ prompt }) => ({ command: "bash -s", stdin: prompt }),
  parseStreamLine: (line) => [{ type: "text", text: `${line}\n` }],
};

const t = (name) => `touch ${MARK}/${name}`;
const PLANT = `
set -eu
cd ${REPO}
echo one >one.txt && git add one.txt && git commit -q -m "honest commit"
hook() { mkdir -p "$(dirname "$1")"; printf '#!/bin/sh\\n%s\\nexit 0\\n' "$2" >"$1"; chmod +x "$1"; }
for h in ${HOOKS.join(" ")}; do
  hook .git/hooks/$h "${t("hook-$h")}"
  hook .git/planted-hooks/$h "${t("hookspath-$h")}"
done
git config core.hooksPath .git/planted-hooks
git config core.fsmonitor "${t("fsmonitor")}; false"
git config core.pager "${t("pager")}"
git config pager.status "${t("pager-status")}"
git config core.editor "${t("editor")}"
git config core.sshCommand "${t("ssh")}"
git config core.askPass "${t("askpass")}"
git config credential.helper "!${t("credential")}"
git config gpg.program "${t("gpg")}"
git config diff.external "${t("diff-external")}"
git config diff.trap.textconv "${t("textconv")}"
git config filter.trap.clean "${t("filter-clean")}; cat"
git config filter.trap.smudge "${t("filter-smudge")}; cat"
git config filter.trap.process "${t("filter-process")}"
git config filter.trap.required true
git config uploadpack.packObjectsHook "${t("pack-objects-hook")}"
git config remote.origin.uploadpack "${t("remote-uploadpack")}"
printf '[core]\\n\\tfsmonitor = ${t("included-fsmonitor")}; false\\n' >.git/planted.gitconfig
git config include.path planted.gitconfig
mkdir -p .git/info && echo '* filter=trap diff=trap' >.git/info/attributes
touch one.txt README.md
echo "PLANTED"
`;
const SECOND = `cd ${REPO} && echo "SECOND $(git log --oneline | wc -l) commits"`;

rmSync(`${E}/lap/traps`, { recursive: true, force: true });
rmSync(MARK, { recursive: true, force: true });
mkdirSync(MARK);
execFileSync(`${WT}/scripts/front-clone`, ["open", REAL, COPY, "traps"], { stdio: "inherit" });

const sandbox = relocated({
  repoPath: REPO,
  imageName: "localhost/sandcastle-pipeline:rig",
  mounts: [{ hostPath: `${E}/config/dev-playbook`, sandboxPath: `${HOME}/workspace/dev-playbook`, readonly: true }],
});
const call = async (prompt, n) => {
  try {
    const r = await run({
      agent: standIn, sandbox, cwd: COPY, prompt, maxIterations: 1,
      branchStrategy: { type: "head" }, logging: { type: "file", path: `${E}/traps-${n}.log` },
    });
    console.log(`call ${n}: commits=${r.commits.length} ${r.stdout.split("\n").filter((l) => /^(PLANTED|SECOND)/.test(l)).join(" ")}`);
  } catch (error) {
    console.log(`call ${n}: THREW ${error.message.split("\n")[0]}`);
  }
};
const fired = () => readdirSync(MARK).sort();

await call(PLANT, 1);
const after1 = fired();
console.log(`FIRED ON HOST after call 1: ${after1.join(", ") || "none"}`);
await call(SECOND, 2);
const after2 = fired().filter((m) => !after1.includes(m));
console.log(`FIRED ON HOST during call 2: ${after2.join(", ") || "none"}`);

// The control: host git in the copy, which is what a trap is for.
spawnSync("git", ["-C", COPY, "status", "--porcelain"], { encoding: "utf8" });
const control = fired().filter((m) => !after1.includes(m) && !after2.includes(m));
console.log(`CONTROL host git status fired: ${control.join(", ") || "none"}`);

const failed = after1.length + after2.length > 0 || control.length === 0;
console.log(failed ? "RESULT FAIL" : "RESULT PASS");
process.exit(failed ? 1 : 0);
