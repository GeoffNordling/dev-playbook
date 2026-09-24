// The resume test: does a principal's conversation carry from one sealed call
// to the next? Call 1, a fresh Sonnet session, is told a magic word in its
// prompt only and writes nothing. Call 2, in a new container, resumes call 1's
// session and is asked the word. A control, a fresh session on the same work
// copy, is asked too: if it knows the word, the word travelled some other way.
// Sandcastle keeps the session file in the stint's own folder, never in the
// user's ~/.claude/projects.
// Run setup.sh on the lab first.
// Usage: node resume.mjs <lab directory>
import { run, claudeCode } from "@ai-hero/sandcastle";
import { execFileSync, spawn, spawnSync } from "node:child_process";
import { copyFileSync, mkdirSync, readdirSync, readFileSync, rmSync } from "node:fs";
import { join } from "node:path";
import { randomInt } from "node:crypto";
import { relocated } from "./relocated.mjs";

const E = process.argv[2];
if (!E) throw new Error("usage: node resume.mjs <lab directory>");
const RIG = import.meta.dirname;
const WT = join(RIG, "../../../..");
const REAL = `${E}/real/mission-control`;
const STINT = `${E}/stint-resume`;
const COPY = `${STINT}/mission-control`;
const SESSIONS = `${STINT}/sessions`;
const CONFIG = `${E}/config/dev-playbook`;
const HOME = "/home/agent";
const REPO = `${HOME}/assignment/mission-control`;
const MODEL = "claude-sonnet-5";
const WORD = `periwinkle${randomInt(1000, 9999)}`;
const USER_PROJECTS = `${process.env.HOME}/.claude/projects`;

rmSync(STINT, { recursive: true, force: true });
mkdirSync(SESSIONS, { recursive: true });
execFileSync(`${WT}/scripts/front-clone`, ["open", REAL, COPY, "resume"], { stdio: "inherit" });
const projectsBefore = new Set(readdirSync(USER_PROJECTS));

const agent = (capture) =>
  claudeCode(MODEL, {
    captureSessions: capture,
    sessionStorage: { hostProjectsDir: SESSIONS },
    env: { CLAUDE_CODE_TMPDIR: "/tmp/agent-tmp" },
  });

// One sealed call, with its own credential copy and hook receiver.
async function call(name, prompt, { capture = true, resumeSession } = {}) {
  const tmp = `${STINT}/call-${name}`;
  mkdirSync(tmp);
  copyFileSync(`${process.env.HOME}/.claude/.credentials.json`, join(tmp, ".credentials.json"));
  const receiver = spawn("python3", [`${RIG}/receiver.py`, join(tmp, "sink")], { stdio: ["ignore", "pipe", "inherit"] });
  await new Promise((ok) => receiver.stdout.once("data", ok));
  const raw = [];
  let result;
  try {
    result = await run({
      agent: agent(capture),
      sandbox: relocated({
        repoPath: REPO,
        imageName: "localhost/sandcastle-pipeline:rig",
        network: "pasta:--map-host-loopback=169.254.1.2",
        mounts: [
          { hostPath: CONFIG, sandboxPath: `${HOME}/workspace/dev-playbook`, readonly: true },
          { hostPath: join(tmp, ".credentials.json"), sandboxPath: `${HOME}/.claude/.credentials.json`, readonly: true },
          { hostPath: join(tmp, "sink"), sandboxPath: `${HOME}/.local/share/claude-measure/sink`, readonly: true },
        ],
      }),
      cwd: COPY,
      prompt,
      resumeSession,
      maxIterations: 1,
      branchStrategy: { type: "head" },
      logging: { type: "file", path: `${STINT}/${name}.log`, onAgentStreamEvent: (ev) => { if (ev.type === "raw") raw.push(ev.line); } },
      idleTimeoutSeconds: 300,
    });
  } finally {
    receiver.kill("SIGTERM");
    await new Promise((ok) => receiver.on("exit", ok));
    rmSync(tmp, { recursive: true, force: true });
  }
  const messages = raw.flatMap((l) => { try { return [JSON.parse(l)]; } catch { return []; } });
  const init = messages.find((m) => m.type === "system" && m.subtype === "init");
  const answer = messages.find((m) => m.type === "result")?.result ?? "";
  const session = result.iterations[0]?.sessionId;
  console.log(`${name}: session=${session} apiKeySource=${init?.apiKeySource} commits=${result.commits.length}`);
  console.log(`${name}: answer=${JSON.stringify(answer.slice(0, 200))}`);
  return { session, answer, commits: result.commits.length, apiKeySource: init?.apiKeySource };
}

const ASK = "What magic word did I give you earlier in this conversation? If you were given none, say NONE. Answer in one line. Do not search files.";
const c1 = await call("call-1", [
  `Remember this magic word: ${WORD}.`,
  "Do not write it anywhere: create no file, edit no file, run no command, make no commit.",
  "Reply with just OK.",
].join("\n"));
const leaked = spawnSync("grep", ["-rl", "--exclude-dir=.git", WORD, COPY], { encoding: "utf8" }).stdout.trim();
console.log(`files holding the word: ${leaked || "none"}`);
const c2 = await call("call-2", ASK, { resumeSession: c1.session });
const control = await call("control", ASK, { capture: false });

const projectsNew = readdirSync(USER_PROJECTS).filter((d) => !projectsBefore.has(d));
const sessionFiles = spawnSync("find", [SESSIONS, "-name", "*.jsonl"], { encoding: "utf8" }).stdout.trim();
console.log(`session files in the stint folder: ${sessionFiles || "none"}`);
console.log(`new folders in ~/.claude/projects: ${projectsNew.join(", ") || "none"}`);

let failed = false;
const fail = (msg) => { failed = true; console.log(`FAIL ${msg}`); };
for (const c of [c1, c2, control]) if (c.apiKeySource !== "none") fail(`billed ${c.apiKeySource}`);
if (leaked) fail("the word reached a file in the work copy");
if (c1.commits + c2.commits + control.commits) fail("a call committed");
if (!c2.answer.includes(WORD)) fail("the resumed call did not name the word");
if (control.answer.includes(WORD)) fail("the control named the word");
if (c2.session !== c1.session) fail(`call 2 ran session ${c2.session}, not call 1's ${c1.session}`);
if (!sessionFiles) fail("no session file in the stint folder");
if (projectsNew.some((d) => d.includes("stint-resume") || d.includes("assignment"))) fail("a session file reached ~/.claude/projects");
const left = spawnSync("podman", ["ps", "-a", "--filter", "ancestor=localhost/sandcastle-pipeline:rig", "-q"], { encoding: "utf8" }).stdout.trim();
if (left) fail(`containers left: ${left.split("\n").length}`);
console.log(failed ? "RESULT FAIL" : "RESULT PASS");
process.exit(failed ? 1 : 0);
