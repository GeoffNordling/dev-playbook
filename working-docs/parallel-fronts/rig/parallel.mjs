// The parallel test: two fronts on one fake real repository, started at the
// same moment, each making one tiny commit on Haiku, then both closed at the
// same moment. Run setup.sh on the lab first.
// Usage: node parallel.mjs <lab directory>
import { run, claudeCode } from "@ai-hero/sandcastle";
import { execFile, spawn, spawnSync } from "node:child_process";
import { copyFileSync, existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { join } from "node:path";
import { promisify } from "node:util";
import { relocated } from "./relocated.mjs";

const E = process.argv[2];
if (!E) throw new Error("usage: node parallel.mjs <lab directory>");
const RIG = import.meta.dirname;
const WT = join(RIG, "../../..");
const REAL = `${E}/real/mission-control`;
const CONFIG = `${E}/config/dev-playbook`;
const HOME = "/home/agent";
const MODEL = "claude-haiku-4-5-20251001";
const FRONTS = ["front-a", "front-b"];
const sh = promisify(execFile);

// The billing guard, applied to everything a run hands in.
const BILLING_ENV_VARS = [
  "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
  "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY",
  "ANTHROPIC_PROFILE", "ANTHROPIC_FEDERATION_RULE_ID", "ANTHROPIC_ORGANIZATION_ID",
];
const CREDENTIAL_SETTINGS_KEYS = ["apiKeyHelper", "awsAuthRefresh", "awsCredentialExport"];
// Lab-only: the lab lives under /tmp/claude-<uid>, which the .git mount makes
// podman create root-owned inside the container, so Claude's temp folder moves.
const agent = claudeCode(MODEL, { captureSessions: false, env: { CLAUDE_CODE_TMPDIR: "/tmp/agent-tmp" } });
const settings = JSON.parse(readFileSync(`${CONFIG}/dotfiles/dot-claude/settings.json`, "utf8"));
const problems = [
  ...BILLING_ENV_VARS.filter((k) => agent.env[k]),
  ...CREDENTIAL_SETTINGS_KEYS.filter((k) => k in settings),
  ...FRONTS.filter((f) => existsSync(`${E}/lap/${f}/mission-control/.sandcastle/.env`)),
];
if (problems.length) throw new Error(`would route to metered billing: ${problems.join(", ")}`);
console.log("GUARD no metered key or setting is handed in");

// One front: its own credential copy, its own receiver, its own run.
async function runFront(front) {
  const copy = `${E}/lap/${front}/mission-control`;
  const tmp = mkdtempSync(`${E}/${front}-`);
  copyFileSync(`${process.env.HOME}/.claude/.credentials.json`, join(tmp, ".credentials.json"));
  const receiver = spawn("python3", [`${RIG}/receiver.py`, join(tmp, "sink")], { stdio: ["ignore", "pipe", "inherit"] });
  receiver.stdout.on("data", (d) => process.stdout.write(`${front} RECEIVER ${d}`));
  await new Promise((ok) => receiver.stdout.once("data", ok));
  const raw = [];
  const started = Date.now();
  let result;
  try {
    result = await run({
      agent,
      sandbox: relocated({
        repoPath: `${HOME}/assignment/mission-control`,
        imageName: "localhost/sandcastle-pipeline:rig",
        network: "pasta:--map-host-loopback=169.254.1.2",
        mounts: [
          { hostPath: CONFIG, sandboxPath: `${HOME}/workspace/dev-playbook`, readonly: true },
          { hostPath: join(tmp, ".credentials.json"), sandboxPath: `${HOME}/.claude/.credentials.json`, readonly: true },
          { hostPath: join(tmp, "sink"), sandboxPath: `${HOME}/.local/share/claude-measure/sink`, readonly: true },
        ],
      }),
      cwd: copy,
      prompt: [
        `Create a file named ${front}.txt containing the line 'Hello from ${front}.'`,
        `Commit it with the message '${front} hello'. Then output <promise>COMPLETE</promise>.`,
      ].join("\n"),
      maxIterations: 1,
      branchStrategy: { type: "head" },
      logging: {
        type: "file",
        path: `${E}/run-${front}.log`,
        onAgentStreamEvent: (ev) => { if (ev.type === "raw") raw.push(ev.line); },
      },
      idleTimeoutSeconds: 300,
    });
  } finally {
    await new Promise((ok) => setTimeout(ok, 3000));
    receiver.kill("SIGTERM");
    await new Promise((ok) => receiver.on("exit", ok));
    rmSync(tmp, { recursive: true, force: true });
  }
  const messages = raw.flatMap((l) => { try { return [JSON.parse(l)]; } catch { return []; } });
  const init = messages.find((m) => m.type === "system" && m.subtype === "init");
  const final = messages.find((m) => m.type === "result");
  return { front, init, final, commits: result.commits, seconds: (Date.now() - started) / 1000 };
}

const runs = await Promise.all(FRONTS.map(runFront));
for (const r of runs) {
  console.log(`${r.front} RUN ${r.seconds.toFixed(0)}s apiKeySource=${r.init?.apiKeySource} session=${r.init?.session_id}`);
  console.log(`${r.front} FINAL ${r.final?.subtype} is_error=${r.final?.is_error} commits=${JSON.stringify(r.commits)}`);
}

// Both closes at the same moment, into the one real repository.
const closes = await Promise.allSettled(
  FRONTS.map((f) => sh(`${WT}/scripts/front-clone`, ["close", `${E}/lap/${f}/mission-control`])),
);
closes.forEach((c, i) => console.log(`${FRONTS[i]} CLOSE ${c.status}${c.status === "rejected" ? ` ${c.reason.stderr || c.reason.message}` : ""}`));

// The checks.
let failed = false;
const fail = (msg) => { failed = true; console.log(`FAIL ${msg}`); };
for (const r of runs) {
  if (r.init?.apiKeySource !== "none") fail(`${r.front} billed ${r.init?.apiKeySource}`);
  const want = r.commits?.at(-1)?.sha;
  const got = spawnSync("git", ["-C", REAL, "rev-parse", "--verify", "--quiet", r.front], { encoding: "utf8" }).stdout.trim();
  console.log(`${r.front} SHA sandbox=${want} real=${got}`);
  if (!want || want !== got) fail(`${r.front} commit did not come back at the same SHA`);
  const q = spawnSync("python3", ["-c",
    "import sqlite3,sys,os;db=sqlite3.connect(os.path.expanduser('~/.local/share/claude-measure/events.db'));"
    + "print(','.join(e for (e,) in db.execute('select event from events where session_id=? order by rowid',(sys.argv[1],))))",
    r.init?.session_id ?? ""], { encoding: "utf8" });
  const events = q.stdout.trim();
  console.log(`${r.front} HOOKS ${events}`);
  for (const need of ["SessionStart", "UserPromptSubmit", "Stop", "SessionEnd"]) {
    if (!events.split(",").includes(need)) fail(`${r.front} hook ${need} not logged`);
  }
}
const left = spawnSync("podman", ["ps", "-a", "--filter", "ancestor=localhost/sandcastle-pipeline:rig", "-q"], { encoding: "utf8" }).stdout.trim();
if (left) fail(`containers left: ${left.split("\n").length}`);
console.log(failed ? "RESULT FAIL" : "RESULT PASS");
process.exit(failed ? 1 : 0);
