// The lifetime test: one work copy, two run() calls in turn, a stand-in agent
// (a shell script, no tokens). Call 1 commits, then leaves residue in every
// place outside a commit it can reach; call 2 reports which residue it sees.
// Only the commit, and anything uncommitted in the work copy, should carry.
// Run setup.sh on the lab first.
// Usage: node lifetime.mjs <lab directory>
import { run } from "@ai-hero/sandcastle";
import { execFileSync } from "node:child_process";
import { rmSync } from "node:fs";
import { join } from "node:path";
import { relocated } from "./relocated.mjs";

const E = process.argv[2];
if (!E) throw new Error("usage: node lifetime.mjs <lab directory>");
const RIG = import.meta.dirname;
const WT = join(RIG, "../../../..");
const REAL = `${E}/real/mission-control`;
const COPY = `${E}/lap/life/mission-control`;
const HOME = "/home/agent";
const REPO = `${HOME}/assignment/mission-control`;

// The stand-in: runs its prompt as a bash script and prints each line of its
// output as text.
const standIn = {
  name: "stand-in",
  env: {},
  captureSessions: false,
  buildPrintCommand: ({ prompt }) => ({ command: "bash -s", stdin: prompt }),
  parseStreamLine: (line) => [{ type: "text", text: `${line}\n` }],
};

const CALL_1 = `
set -eu
cd ${REPO}
echo "CONTAINER $HOSTNAME"
echo one >one.txt && git add one.txt && git commit -q -m "call 1"
echo home >${HOME}/residue-home
echo tmp >/tmp/residue-tmp
git config --global residue.key call1
nohup sleep 600 >/dev/null 2>&1 &
echo stray >stray.txt
echo "CALL1 DONE"
`;

const CALL_2 = `
cd ${REPO}
echo "CONTAINER $HOSTNAME"
seen() { if eval "$2"; then echo "CARRIED $1"; else echo "GONE $1"; fi; }
seen commit        '[ -f one.txt ] && git log --format=%s | grep -qx "call 1"'
seen home-file     '[ -e ${HOME}/residue-home ]'
seen tmp-file      '[ -e /tmp/residue-tmp ]'
seen git-global    'git config --global residue.key >/dev/null'
seen process       'pgrep -f "sleep 600" >/dev/null'
seen stray-file    '[ -e stray.txt ]'
echo "CALL2 DONE"
`;

rmSync(`${E}/lap/life`, { recursive: true, force: true });
execFileSync(`${WT}/scripts/front-clone`, ["open", REAL, COPY, "life"], { stdio: "inherit" });

const sandbox = relocated({
  repoPath: REPO,
  imageName: "localhost/sandcastle-pipeline:rig",
  mounts: [{ hostPath: `${E}/config/dev-playbook`, sandboxPath: `${HOME}/workspace/dev-playbook`, readonly: true }],
});
const call = (prompt, n) =>
  run({
    agent: standIn,
    sandbox,
    cwd: COPY,
    prompt,
    maxIterations: 1,
    branchStrategy: { type: "head" },
    logging: { type: "file", path: `${E}/life-${n}.log` },
  });

const lines = (r) => r.stdout.split("\n").filter((l) => /^(CONTAINER|CARRIED|GONE|CALL)/.test(l));
const r1 = await call(CALL_1, 1);
console.log(`call 1: commits=${JSON.stringify(r1.commits)} preserved=${r1.preservedWorktreePath}`);
lines(r1).forEach((l) => console.log(`  ${l}`));
const r2 = await call(CALL_2, 2);
console.log(`call 2: commits=${JSON.stringify(r2.commits)} preserved=${r2.preservedWorktreePath}`);
lines(r2).forEach((l) => console.log(`  ${l}`));

// The expectation: a new container each call, and only the work copy carries.
const want = { commit: "CARRIED", "stray-file": "CARRIED", "home-file": "GONE", "tmp-file": "GONE", "git-global": "GONE", process: "GONE" };
const got = Object.fromEntries(lines(r2).filter((l) => /^(CARRIED|GONE)/.test(l)).map((l) => l.split(" ").reverse()));
const containers = [r1, r2].map((r) => lines(r).find((l) => l.startsWith("CONTAINER")));
let failed = false;
if (containers[0] === containers[1]) { failed = true; console.log(`FAIL one container for both calls: ${containers[0]}`); }
for (const [k, v] of Object.entries(want)) {
  if (got[k] !== v) { failed = true; console.log(`FAIL ${k}: want ${v}, got ${got[k]}`); }
}
const left = execFileSync("podman", ["ps", "-a", "--filter", "ancestor=localhost/sandcastle-pipeline:rig", "-q"], { encoding: "utf8" }).trim();
if (left) { failed = true; console.log(`FAIL containers left: ${left.split("\n").length}`); }
console.log(failed ? "RESULT FAIL" : "RESULT PASS");
process.exit(failed ? 1 : 0);
