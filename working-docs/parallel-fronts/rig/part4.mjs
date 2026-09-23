// Experiment three, part 4: real Claude, on the subscription, one tiny task,
// through the option B plug-in, work copy at /home/agent/assignment/<repo>.
// Usage: node part4.mjs
import { run, claudeCode } from "@ai-hero/sandcastle";
import { spawn } from "node:child_process";
import { copyFileSync, existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { join } from "node:path";
import { relocated } from "./relocated.mjs";

const E = "/tmp/claude-1000/-home-geoff-workspace-dev-playbook/a7e4c307-11ae-41f0-a856-c762525f0982/scratchpad/exp3";
const COPY = `${E}/lap/front-a/mission-control`;
const CONFIG = `${E}/config/dev-playbook`;
const HOME = "/home/agent";
// DIAG=1: the cheapest model, a one-word task, and Claude's hook debug log
// printed after the run, to see what becomes of Stop and SessionEnd.
const DIAG = process.env.DIAG === "1";
const MODEL = DIAG ? "claude-haiku-4-5-20251001" : "claude-sonnet-5";

// The prototype's billing guard, applied to everything this run hands in.
const BILLING_ENV_VARS = [
  "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
  "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY",
  "ANTHROPIC_PROFILE", "ANTHROPIC_FEDERATION_RULE_ID", "ANTHROPIC_ORGANIZATION_ID",
];
const CREDENTIAL_SETTINGS_KEYS = ["apiKeyHelper", "awsAuthRefresh", "awsCredentialExport"];

// Rig-only: the copies live under /tmp/claude-1000, so the .git mount makes
// podman create that directory, root-owned, inside the container, and Claude
// refuses its default temp directory. Real copies will not live there.
const claude = claudeCode(MODEL, { captureSessions: false, env: { CLAUDE_CODE_TMPDIR: "/tmp/agent-tmp" } });
// The end-of-session fix: Claude's Stop and SessionEnd hooks run in the
// background after it exits, so hold the sandbox open 5 s for them to send,
// then return Claude's own exit status.
const agent = {
  ...claude,
  buildPrintCommand: (o) => {
    const c = claude.buildPrintCommand(o);
    if (!DIAG) return { ...c, command: `${c.command}; s=$?; sleep 5; exit $s` };
    const cmd = c.command.replace("claude --print", "claude --debug hooks --debug-file /tmp/claude-debug.log --print");
    return { ...c, command: `${cmd}; s=$?; sleep 5; grep -iE 'stop|sessionend|session_end|hook' /tmp/claude-debug.log | sed 's/^/DIAG /' | tail -60; cat ~/.local/share/claude-measure/errors.log 2>/dev/null | sed 's/^/HOOKERR /'; exit $s` };
  },
};
const settings = JSON.parse(readFileSync(`${CONFIG}/dotfiles/dot-claude/settings.json`, "utf8"));
const problems = [
  ...BILLING_ENV_VARS.filter((k) => agent.env[k]),
  ...CREDENTIAL_SETTINGS_KEYS.filter((k) => k in settings),
  ...(existsSync(`${COPY}/.sandcastle/.env`) ? [".sandcastle/.env in the copy"] : []),
];
if (problems.length) throw new Error(`would route to metered billing: ${problems.join(", ")}`);
console.log("GUARD no metered key or setting is handed in");

// The credential and the sink file, both copies in a directory deleted at the end.
const tmp = mkdtempSync(`${E}/part4-`);
copyFileSync(`${process.env.HOME}/.claude/.credentials.json`, join(tmp, ".credentials.json"));
const receiver = spawn("python3", [`${E}/receiver.py`, join(tmp, "sink")], { stdio: ["ignore", "pipe", "inherit"] });
receiver.stdout.on("data", (d) => process.stdout.write(`RECEIVER ${d}`));
await new Promise((ok) => receiver.stdout.once("data", ok));

const raw = [];
const prompt = DIAG ? "Reply with the single word hi, then output <promise>COMPLETE</promise>." : [
  "You are inside a podman container. Your checkout is the current directory.",
  "Do two things:",
  "1. Append the line 'Hello from the sandbox.' to README.md and commit it with the message 'sandbox hello'.",
  "2. In your final message, name three of the skills available to you.",
  "When done, output <promise>COMPLETE</promise>.",
].join("\n");

let result;
try {
  result = await run({
    agent,
    sandbox: relocated({
      repoPath: `${HOME}/assignment/mission-control`,
      imageName: "localhost/sandcastle-probe:exp3",
      network: "pasta:--map-host-loopback=169.254.1.2",
      mounts: [
        { hostPath: CONFIG, sandboxPath: `${HOME}/workspace/dev-playbook`, readonly: true },
        { hostPath: join(tmp, ".credentials.json"), sandboxPath: `${HOME}/.claude/.credentials.json`, readonly: true },
        { hostPath: join(tmp, "sink"), sandboxPath: `${HOME}/.local/share/claude-measure/sink`, readonly: true },
      ],
    }),
    cwd: COPY,
    prompt,
    maxIterations: 1,
    branchStrategy: { type: "head" },
    logging: {
      type: "file",
      path: `${E}/run-part4.log`,
      onAgentStreamEvent: (ev) => { if (ev.type === "raw") raw.push(ev.line); },
    },
    idleTimeoutSeconds: 300,
  });
} finally {
  // Let async hooks that fired at the end finish arriving, then stop.
  await new Promise((ok) => setTimeout(ok, 5000));
  receiver.kill("SIGTERM");
  await new Promise((ok) => receiver.on("exit", ok));
  rmSync(tmp, { recursive: true, force: true });
}

const messages = raw.flatMap((l) => { try { return [JSON.parse(l)]; } catch { return []; } });
for (const l of raw) if (/^(DIAG|HOOKERR) /.test(l)) console.log(l.slice(0, 260));
const init = messages.find((m) => m.type === "system" && m.subtype === "init");
const final = messages.find((m) => m.type === "result");
console.log("INIT apiKeySource:", init?.apiKeySource, " model:", init?.model, " session:", init?.session_id);
console.log("INIT cwd:", init?.cwd);
console.log("INIT skills:", init?.skills?.length, " agents:", init?.agents?.length);
console.log("FINAL:", final?.subtype, "is_error:", final?.is_error, "turns:", final?.num_turns);
console.log("FINAL text:", final?.result);
console.log("RESULT commits:", JSON.stringify(result.commits));
if (init?.apiKeySource !== "none") throw new Error(`billed ${init?.apiKeySource}, not the subscription`);
