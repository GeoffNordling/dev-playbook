// The stint's only Node code: what needs Sandcastle, and nothing else.
//
// Reads one request as JSON on stdin, from dev_playbook.stint.call. Its `job`
// is `agent` or `check`, and each run below is Sandcastle's run() in a new
// container on the work copy.
//
// An agent job runs three times: first the gate's setup, which installs the
// repository's pre-commit hooks in the copy and builds their environments;
// then the agent; then a probe that lists the files the agent left
// uncommitted. Its response:
//
//   session   the agent's Claude session ID
//   usage     the token use at its last turn, as Sandcastle reports it
//   commits   the SHAs the agent committed, oldest first
//   raw       Claude's raw stream, one JSON line each
//   probe     git's short status lines for the work copy
//
// A check job runs the stint's target check, a shell command that spends no
// tokens, then the probe. Its response:
//
//   exit      the command's exit code
//   output    its stdout and stderr, one line each
//   probe     git's short status lines for the work copy
//
// Prints the response as JSON on stdout's last line. Every choice about what
// is mounted, billed, or kept is the caller's.
import { run, claudeCode } from "@ai-hero/sandcastle";
import { readFileSync } from "node:fs";
import { relocated } from "./relocated.mjs";

const COMMON = ["job", "copy", "repo", "image", "network", "mounts", "log", "probeLog"];
const KEYS = {
  agent: [...COMMON, "env", "sessions", "setupLog", "model", "prompt", "resume"],
  check: [...COMMON, "command"],
};
const req = JSON.parse(readFileSync(0, "utf8"));
if (!(req.job in KEYS)) throw new Error(`run.mjs: unknown job ${req.job}`);
const missing = KEYS[req.job].filter((k) => !(k in req));
if (missing.length) throw new Error(`run.mjs: request lacks ${missing.join(", ")}`);

const sandbox = relocated({
  repoPath: req.repo,
  imageName: req.image,
  network: req.network,
  mounts: req.mounts,
});
// A shell command as a run's agent, for the setup, the probe, and the check.
// Sandcastle runs it in the work copy with sh -c and fails the run on a
// nonzero exit.
const shell = (name, command) => ({
  name,
  env: {},
  captureSessions: false,
  buildPrintCommand: () => ({ command }),
  parseStreamLine: (line) => [{ type: "text", text: `${line}\n` }],
});
const once = { sandbox, cwd: req.copy, maxIterations: 1, branchStrategy: { type: "head" } };
const probe = shell("probe", `git -C ${req.repo} status --porcelain --untracked-files=all`);
const probeRun = () => run({ ...once, agent: probe, prompt: "probe", logging: { type: "file", path: req.probeLog } });

if (req.job === "check") {
  // A nonzero exit is findings, not a failed run, so the wrapper exits 0 and
  // prints the command's exit code on a last line of its own.
  const MARK = "stint-check-exit=";
  const check = shell("check", `(${req.command}) 2>&1; echo "${MARK}$?"`);
  const checked = await run({ ...once, agent: check, prompt: "check", logging: { type: "file", path: req.log } });
  const probed = await probeRun();
  const lines = checked.stdout.replace(/\n$/, "").split("\n");
  const last = lines.pop();
  if (!last?.startsWith(MARK)) throw new Error(`run.mjs: the check's last line is not its exit code: ${last}`);
  console.log(JSON.stringify({
    exit: Number(last.slice(MARK.length)),
    output: lines,
    probe: probed.stdout.split("\n"),
  }));
} else {
  const agent = claudeCode(req.model, {
    captureSessions: true,
    sessionStorage: { hostProjectsDir: req.sessions },
    env: req.env,
  });
  // The hooks go in the copy's .git and their environments in the cache
  // mount, both of which outlive the container; installing on every call also
  // puts back a hook an earlier call removed.
  const setup = shell("setup", "pre-commit install --install-hooks");
  await run({ ...once, agent: setup, prompt: "setup", logging: { type: "file", path: req.setupLog } });
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
  const probed = await probeRun();

  const [iteration] = result.iterations;
  if (!iteration?.sessionId) throw new Error("run.mjs: the agent's run reported no session");
  console.log(JSON.stringify({
    session: iteration.sessionId,
    usage: iteration.usage ?? null,
    commits: result.commits.map((c) => c.sha),
    raw,
    probe: probed.stdout.split("\n"),
  }));
}
