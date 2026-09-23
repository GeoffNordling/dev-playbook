// Option B: Sandcastle's own podman plug-in, with the repository's mount
// moved from the /home/agent/workspace Sandcastle suggests to `repoPath`.
// Sandcastle then works wherever the plug-in reports the repository to be.
import { createBindMountSandboxProvider } from "@ai-hero/sandcastle";
import { podman } from "@ai-hero/sandcastle/sandboxes/podman";

export const relocated = ({ repoPath, ...podmanOptions }) => {
  const inner = podman(podmanOptions);
  return createBindMountSandboxProvider({
    name: "podman-relocated",
    env: inner.env,
    sandboxHomedir: inner.sandboxHomedir,
    create: (options) =>
      inner.create({
        ...options,
        mounts: options.mounts.map((m) =>
          m.hostPath === options.worktreePath ? { ...m, sandboxPath: repoPath } : m,
        ),
      }),
  });
};
