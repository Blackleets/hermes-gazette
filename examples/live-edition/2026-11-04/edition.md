# 📰 The Hermes Gazette
*The newspaper of the Nous Research ecosystem*
**2026-11-04** · 12 stories

## Under the Hood
### [A running request is not "busy with an earlier turn"; …](https://github.com/NousResearch/hermes-agent/commit/3a1e9ef50a570b1544795ddad197ad2dcde430ab)
_Hermes Agent — Commits · 2026-11-04_
Trim the message_agent schema Live: the deliver answer reads target_state "working" for the turn this same request just started, so the ack no longer claims an earlier turn.

### [Typed request envelope, a forgotten reply relayed onc…](https://github.com/NousResearch/hermes-agent/commit/160339e0dd5ceb4fe5b1feadf26e0886028bb9ab)
_Hermes Agent — Commits · 2026-11-04_
And one "never answered" sentence per dead request - message_agent takes optional constraints and expecting; the teammate reads them as labelled "Constraints:" / "Reply needed:" lines under the message.; A teammate that ends a request turn…

### [A fan-out to a peer and a local bot sharing its name r…](https://github.com/NousResearch/hermes-agent/commit/53f5378a8e8271e3b0cace624c0805c63e30f6bd)
_Hermes Agent — Commits · 2026-11-04_
Both split_targets deduplicated a comma list by the local bot each name resolves to.

### [A sender's cancel by delivery id always reaches the de…](https://github.com/NousResearch/hermes-agent/commit/50c7d1c4b9cc01e5dccb66dfab9ac38066779627)
_Hermes Agent — Commits · 2026-11-04_
Retry message_agent's cancel picked an admission from the target's receipt file and cancelled it with prompt.cancel.

### [Fan-out keeps every teammate's answer, error and pendi…](https://github.com/NousResearch/hermes-agent/commit/303f2a8035dc9aa0048c8de6799e88811423bffd)
_Hermes Agent — Commits · 2026-11-04_
State Review round on the message_agent fan-out: The runner's sub-processes get stdin=DEVNULL (the TUI subprocess stdin guard).; Each spec entry names how its runner reports: only the live lane prints a delivery record; a relay or peer…

### [Cover the teammate state a message_agent sender hears](https://github.com/NousResearch/hermes-agent/commit/5c75b00d0aa28caa445d67bdf69b3867742726d1)
_Hermes Agent — Commits · 2026-11-04_
Idle / working / waiting_clarify / waiting_approval (approval first) / paused, derived by gateway/session_bot_state.py from a real SessionAuthority, claim and prompt registration.

## Hermes Agent
### [Hermes Agent v0.22.7 released](https://github.com/NousResearch/hermes-agent/releases/tag/v0.22.7%2Bcanary.20261104T064347Z)
_Hermes Agent — Releases · 2026-11-04_
Hermes Agent canary 20261104T064347Z

### [Hermes Agent v0.22.7](https://github.com/NousResearch/hermes-agent/releases/tag/v0.22.7)
_Hermes Agent — Releases · 2026-11-03_
Patch release. This tag rolls up the ~174 PRs merged since v0.22.6 into a stable release for the GitHub release (CLI and installers), the Microsoft Store app, Docker and Hermes Cloud.

### [Hermes Agent v0.22.7 — release candidate 1](https://github.com/NousResearch/hermes-agent/releases/tag/rc.1-v0.22.7)
_Hermes Agent — Releases · 2026-11-03_
Pre-release build for testing.

### [Hermes Agent v0.22.6 released](https://github.com/NousResearch/hermes-agent/releases/tag/v0.22.6%2Bcanary.20261103T064339Z)
_Hermes Agent — Releases · 2026-11-03_
Hermes Agent canary 20261103T064339Z

### [Hermes Agent v0.22.6](https://github.com/NousResearch/hermes-agent/releases/tag/v0.22.6)
_Hermes Agent — Releases · 2026-11-02_
Patch release. This tag rolls up the ~776 PRs merged since v0.22.5 into a stable release for the GitHub release (CLI and installers), the Microsoft Store app, Docker and Hermes Cloud.

### [Hermes Agent v0.22.6 — release candidate 3](https://github.com/NousResearch/hermes-agent/releases/tag/rc.3-v0.22.6)
_Hermes Agent — Releases · 2026-11-02_
Pre-release build for testing.
