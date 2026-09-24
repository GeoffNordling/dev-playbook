// One sealed call: one Claude session in a new container on a stint's work
// copy, then a probe in another new container that reports whether the call
// left work uncommitted. The step a driver repeats for every iteration, every
// review, and every turn of the principal.
//
// Usage: node call.mjs <options JSON file>
//   lab        the lab directory setup.sh filled (config copy, image)
//   copy       the stint's work copy, opened by front-clone
//   stint      the stint's folder on the host: session files, logs, call records
//   name       this call's name, such as iter-1; names its log and record
//   model      the Claude model
//   prompt     the prompt text
//   resume     optional: a session ID to resume; omitted means a fresh session
//
// Writes <stint>/calls/<name>.json: the session ID, the final answer, the
// commits, the billing source, and the uncommitted files, and prints it.
// Never runs git on the host in the copy.
import { run, claudeCode } from "@ai-hero/sandcastle";
import { spawn } from "node:child_process";
import { copyFileSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";
import { relocated } from "./relocated.mjs";

const opts = JSON.parse(readFileSync(process.argv[2], "utf8"));
for (const k of ["lab", "copy", "stint", "name", "model", "prompt"]) {
  if (!opts[k]) throw new Error(`call.mjs: missing option ${k}`);
}
const RIG = import.meta.dirname;
const HOME = "/home/agent";
const REPO = `${HOME}/assignment/${basename(opts.copy)}`;
const CONFIG = `${opts.lab}/config/dev-playbook`;
const CALLS = `${opts.stint}/calls`;
mkdirSync(CALLS, { recursive: true });

// The billing guard, applied to everything a call hands in.
const BILLING_ENV_VARS = [
  "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
  "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY",
  "ANTHROPIC_PROFILE", "ANTHROPIC_FEDERATION_RULE_ID", "ANTHROPIC_ORGANIZATION_ID",
];
const CREDENTIAL_SETTINGS_KEYS = ["apiKeyHelper", "awsAuthRefresh", "awsCredentialExport"];
const agent = claudeCode(opts.model, {
  captureSessions: true,
  sessionStorage: { hostProjectsDir: `${opts.stint}/sessions` },
  // The lab lives under /tmp/claude-<uid>, which the .git mount makes
  // root-owned inside the container, so Claude's temp folder moves.
  env: { CLAUDE_CODE_TMPDIR: "/tmp/agent-tmp" },
});
const settings = JSON.parse(readFileSync(`${CONFIG}/dotfiles/dot-claude/settings.json`, "utf8"));
const problems = [
  ...BILLING_ENV_VARS.filter((k) => agent.env[k]),
  ...CREDENTIAL_SETTINGS_KEYS.filter((k) => k in settings),
];
if (problems.length) throw new Error(`would route to metered billing: ${problems.join(", ")}`);

// The probe: a shell script instead of Claude, no tokens.
const probe = {
  name: "probe",
  env: {},
  captureSessions: false,
  buildPrintCommand: () => ({ command: `git -C ${REPO} status --porcelain --untracked-files=all` }),
  parseStreamLine: (line) => [{ type: "text", text: `${line}\n` }],
};

const tmp = `${opts.stint}/tmp-${opts.name}`;
rmSync(tmp, { recursive: true, force: true });
mkdirSync(tmp);
copyFileSync(`${process.env.HOME}/.claude/.credentials.json`, join(tmp, ".credentials.json"));
const receiver = spawn("python3", [`${RIG}/receiver.py`, join(tmp, "sink")], { stdio: ["ignore", "pipe", "inherit"] });
await new Promise((ok) => receiver.stdout.once("data", ok));
const sandbox = relocated({
  repoPath: REPO,
  imageName: "localhost/sandcastle-pipeline:rig",
  network: "pasta:--map-host-loopback=169.254.1.2",
  mounts: [
    { hostPath: CONFIG, sandboxPath: `${HOME}/workspace/dev-playbook`, readonly: true },
    { hostPath: join(tmp, ".credentials.json"), sandboxPath: `${HOME}/.claude/.credentials.json`, readonly: true },
    { hostPath: join(tmp, "sink"), sandboxPath: `${HOME}/.local/share/claude-measure/sink`, readonly: true },
  ],
});

const raw = [];
const started = Date.now();
let result, dirty;
try {
  result = await run({
    agent,
    sandbox,
    cwd: opts.copy,
    prompt: opts.prompt,
    resumeSession: opts.resume,
    maxIterations: 1,
    branchStrategy: { type: "head" },
    logging: {
      type: "file",
      path: `${CALLS}/${opts.name}.log`,
      onAgentStreamEvent: (ev) => { if (ev.type === "raw") raw.push(ev.line); },
    },
    idleTimeoutSeconds: 900,
  });
  const probed = await run({
    agent: probe, sandbox, cwd: opts.copy, prompt: "probe", maxIterations: 1,
    branchStrategy: { type: "head" }, logging: { type: "file", path: `${CALLS}/${opts.name}-probe.log` },
  });
  dirty = probed.stdout.split("\n").filter((l) => /^.. /.test(l));
} finally {
  receiver.kill("SIGTERM");
  await new Promise((ok) => receiver.on("exit", ok));
  rmSync(tmp, { recursive: true, force: true });
}

const messages = raw.flatMap((l) => { try { return [JSON.parse(l)]; } catch { return []; } });
const init = messages.find((m) => m.type === "system" && m.subtype === "init");
const final = messages.find((m) => m.type === "result");
const record = {
  name: opts.name,
  session: result.iterations[0]?.sessionId,
  resumed: opts.resume ?? null,
  apiKeySource: init?.apiKeySource,
  seconds: Math.round((Date.now() - started) / 1000),
  isError: final?.is_error,
  usage: result.iterations[0]?.usage,
  commits: result.commits.map((c) => c.sha),
  uncommitted: dirty,
  answer: final?.result ?? "",
};
writeFileSync(`${CALLS}/${opts.name}.json`, JSON.stringify(record, null, 2));
console.log(JSON.stringify(record, null, 2));
if (record.apiKeySource !== "none") {
  console.error(`call.mjs: billed ${record.apiKeySource}`);
  process.exit(2);
}
