# Harness recipes

Reusable patterns — recipes — for getting leverage out of the Claude Code harness.

> *"The future is already here. It's just not evenly distributed."*  
> — William Gibson
>
> *"This 'telephone' has too many shortcomings to be seriously considered as a means of communication. The device is inherently of no value to us."*  
> — Internal Western Union memo, 1876
>
> *"Keep your eyes on the goal, and just keep taking the next step towards completing it. If you aren't sure which way to do something, do it both ways and see which works better."*  
> — John Carmack

## Subscription billing constraint

We recognize programatic, API-based workflows as a supremely-powerful pattern in agentic development. Alas, as a private individual with very limited funding, we're restricted to subscription billing. Anthropic limits that to "interactive" Claude Code sessions only.

In June 2026, Anthropic announced moving Agent SDK and `claude -p` usage off the subscription pool, then [paused the change](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan). We treat the pause as temporary; Anthropic has a tendency to pull the rug out on customers.

## Recipes

| Recipe | Purpose |
|--------|---------|
| [Ralph loop](recipes/ralph-loop.md) | Grind a large, sequentially-decomposable goal to done by booting a fresh agent each iteration. |
