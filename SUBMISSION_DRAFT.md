---
title: GhostLog — The Repo That Talks to the Dead
published: false
tags: devchallenge, hf26challenge
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26)*

## What I Built

GhostLog is a small app that reads a git repository's commit history
and turns it into a short, atmospheric ghost story — in the spirit of
Día de los Muertos — written by a locally-running open-weight AI model.

It pays special attention to commits made during the **"witching
hour"** (midnight–4am): the late-night pushes, the 2am bug fixes, the
half-asleep refactors. Those commits get woven into the story as the
most restless spirits, because — let's be honest — most of us have
shipped something we shouldn't have at 2am.

<!-- TODO: 1-2 sentences on what inspired this specific idea, in your
own words. E.g. "I kept thinking about how a repo's git blame is kind
of already a graveyard of past selves..." -->

## Demo

<!-- TODO: paste a deployed link OR a short screen-recording/GIF here.
A free option: record with your OS's built-in screen recorder (Win+Alt+R
on Windows, Cmd+Shift+5 on Mac), trim it, and drag the file into this
editor — DEV.to will host it inline. -->

## Code

{% github YOUR_GITHUB_USERNAME/ghostlog %}

<!-- TODO: replace with your actual repo slug once pushed. The {% github %}
liquid tag above auto-embeds the repo card when the post is published. -->

## How I Built It

GhostLog is a Python + [Streamlit](https://streamlit.io) app, built in
two small pieces:

- **`ghost_story.py`** shells out to `git log` to pull recent commits
  (hash, author, timestamp, message), flags the ones that landed in
  the midnight–4am window, and assembles a prompt that hands all of
  that real history to the model with instructions to write a short
  story grounded in it — not a generic one.
- **`app.py`** is the Streamlit front end: point it at a repo path,
  hit "Summon the Ghosts," and it shows the story alongside the raw
  commit list it was built from.

The AI side runs entirely on **[Ollama](https://ollama.com)**, serving
Google's open-weight **Gemma** model locally. No cloud API, no key, no
account.

<!-- TODO: swap in any real details that changed once you've actually
built/tweaked it — e.g. if you used Antigravity to scaffold or extend
parts of this, mention that here. -->

## Why Does Open Innovation Matter?

Three reasons this had to be open-weight and local, not a closed API:

1. **Privacy.** Commit history can be sensitive — author names,
   internal feature names, things said in a 2am commit message you'd
   rather a third-party API never saw. Running locally means your
   repo's history never leaves your machine.
2. **Works with the lights off.** Once the model is pulled, GhostLog
   needs zero internet connection. No API outage, no rate limit, no
   "service temporarily unavailable" mid-demo.
3. **No lock-in.** Swapping Gemma for Llama 3, Mistral, or any other
   Ollama-hosted model is a one-line change in the sidebar — not a
   rewrite, not a new account, not a new bill.

<!-- TODO: add your own honest take here too — did the open-weight
approach actually work *better* than you expected, or were there
trade-offs (slower, needed more prompt-tuning)? Judges want the real
story. -->

## My Agent Session

<!-- Optional, but judges love it. If you used Antigravity, Claude, or
another agent to help build this, save/export the session and link it
or embed it here with the agent_session tag per the challenge page. -->

## The Spirit of It

<!-- Optional. Run GhostLog on your OWN project's repo once it's done —
if the story it tells actually gives you a chill, or surfaces a commit
message that makes you laugh, put that moment here. This is the
section that makes a submission memorable to judges. -->

## Prize Categories

- Gemma (ran the open-weight model locally via Ollama)

<!-- TODO: add any other partner categories you end up using, e.g. if
you deploy a hosted demo on Render, add Render too. Check the full
list of 20 categories on the HF26 DEV Challenge Hub. -->
