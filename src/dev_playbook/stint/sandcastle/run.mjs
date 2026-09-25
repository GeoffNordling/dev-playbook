// The stint's only Node code: what needs Sandcastle, and nothing else.
//
// Reads one request as JSON on stdin, from dev_playbook.stint.call. Runs
// Sandcastle's run() twice, each in a new container on the work copy: first
// the agent, then a probe that lists the files the agent left uncommitted.
// Prints one response as JSON on stdout's last line:
//
//   session   the agent's Claude session ID
//   usage     the token use at its last turn, as Sandcastle reports it
//   commits   the SHAs the agent committed, oldest first
//   raw       Claude's raw stream, one JSON line each
//   probe     git's short status lines for the work copy
//
// Every choice about what is mounted, billed, or kept is the caller's.
import { run, claudeCode } from "@ai-hero/sandcastle";
import { readFileSync } from "node:fs";
import { relocated } from "./relocated.mjs";

const KEYS = ["copy", "repo", "image", "network", "mounts", "env", "sessions", "log", "probeLog", "model", "prompt", "resume"];
const req = JSON.parse(readFileSync(0, "utf8"));
const missing = KEYS.filter((k) => !(k in req));
if (missing.length) throw new Error(`run.mjs: request lacks ${missing.join(", ")}`);

const sandbox = relocated({
  repoPath: req.repo,
  imageName: req.image,
  network: req.network,
  mounts: req.mounts,
});
const agent = claudeCode(req.model, {
  captureSessions: true,
  sessionStorage: { hostProjectsDir: req.sessions },
  env: req.env,
});
// A shell command in place of Claude: no tokens.
const probe = {
  name: "probe",
  env: {},
  captureSessions: false,
  buildPrintCommand: () => ({ command: `git -C ${req.repo} status --porcelain --untracked-files=all` }),
  parseStreamLine: (line) => [{ type: "text", text: `${line}\n` }],
};
const once = { sandbox, cwd: req.copy, maxIterations: 1, branchStrategy: { type: "head" } };

const raw = [];
const result = await run({
  ...once,
  agent,
  prompt: req.prompt,
  resumeSession: req.resume ?? undefined,
  idleTimeoutSeconds: 900,
  logging: {
    type: "file",
    path: req.log,
    onAgentStreamEvent: (ev) => { if (ev.type === "raw") raw.push(ev.line); },
  },
});
const probed = await run({ ...once, agent: probe, prompt: "probe", logging: { type: "file", path: req.probeLog } });

const [iteration] = result.iterations;
if (!iteration?.sessionId) throw new Error("run.mjs: the agent's run reported no session");
console.log(JSON.stringify({
  session: iteration.sessionId,
  usage: iteration.usage ?? null,
  commits: result.commits.map((c) => c.sha),
  raw,
  probe: probed.stdout.split("\n"),
}));
