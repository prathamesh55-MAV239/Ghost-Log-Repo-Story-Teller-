"""
ghost_story.py
---------------
Core logic for GhostLog: pulls a git repo's commit history, finds the
"witching hour" commits (made late at night), and asks a locally-running
open-weight model (via Ollama) to turn that history into a short, spooky
Day of the Dead-flavored story about what happened in the codebase while
everyone was asleep.

No code, commit messages, or diffs ever leave the machine: the model
runs locally through Ollama, so this works fully offline and keeps
whatever repo you point it at completely private.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

try:
    import ollama
except ImportError:  # pragma: no cover - surfaced nicely in the UI instead
    ollama = None


WITCHING_HOUR_START = 0   # 12:00 AM
WITCHING_HOUR_END = 4     # 4:00 AM, inclusive


@dataclass
class Commit:
    short_hash: str
    author: str
    date: datetime
    message: str

    @property
    def is_witching_hour(self) -> bool:
        return WITCHING_HOUR_START <= self.date.hour <= WITCHING_HOUR_END


class GhostLogError(Exception):
    """Raised for anything GhostLog can't recover from gracefully."""


def get_commit_log(repo_path: str, limit: int = 40) -> List[Commit]:
    """Return the most recent `limit` commits from a local git repo."""
    if not repo_path:
        raise GhostLogError("No repository path was given.")

    # %x1f / %x1e are unlikely-to-collide field/record separators.
    fmt = "%h%x1f%an%x1f%aI%x1f%s%x1e"
    cmd = ["git", "log", f"-n{limit}", f"--pretty=format:{fmt}"]

    import os

    if not os.path.isdir(repo_path):
        raise GhostLogError(f"'{repo_path}' isn't a folder that exists.")

    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except FileNotFoundError as exc:
        raise GhostLogError(
            "git isn't installed or isn't on PATH."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise GhostLogError("Reading the git log timed out.") from exc

    if result.returncode != 0:
        raise GhostLogError(
            f"'{repo_path}' doesn't look like a git repository "
            f"(git said: {result.stderr.strip() or 'unknown error'})."
        )

    commits: List[Commit] = []
    for record in result.stdout.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        parts = record.split("\x1f")
        if len(parts) != 4:
            continue
        short_hash, author, iso_date, message = parts
        try:
            date = datetime.fromisoformat(iso_date)
        except ValueError:
            continue
        commits.append(Commit(short_hash, author, date, message))

    if not commits:
        raise GhostLogError(
            "No commits found. Is this an empty repo, or the wrong path?"
        )

    return commits


def build_prompt(commits: List[Commit], repo_name: str) -> str:
    """Craft the prompt that turns raw commits into a ghost story."""
    witching = [c for c in commits if c.is_witching_hour]

    lines = []
    for c in commits:
        tag = " [WITCHING HOUR]" if c.is_witching_hour else ""
        lines.append(
            f"- {c.date.strftime('%Y-%m-%d %H:%M')} | {c.author} | "
            f"\"{c.message}\"{tag}"
        )
    commit_block = "\n".join(lines)

    witching_note = (
        f"{len(witching)} of these commits were made between midnight "
        "and 4am — the witching hour. Give those commits special "
        "weight in the story: they are the restless spirits most active "
        "while the rest of the codebase slept."
        if witching
        else "No commits happened during the witching hour this time — "
        "this repo's ghosts keep respectable hours. Lean instead into "
        "quieter, more melancholic hauntings: old code as half-remembered "
        "ancestors."
    )

    return f"""You are a folk storyteller in the Dia de los Muertos tradition,
but your graveyard is a git repository. Write a short, atmospheric story
(250-350 words) about the spirits haunting the codebase "{repo_name}".

Ground rules:
- Treat each commit as a small haunting: a spirit leaving a trace.
- Weave in the ACTUAL author names and commit messages below — don't
  invent fake ones. You may paraphrase or lightly embellish, but the
  story should clearly be built from this real history.
- {witching_note}
- Tone: eerie but warm, closer to an ofrenda and a campfire story than
  outright horror. Reference marigolds, candlelight, or returning
  spirits if it fits naturally — don't force it.
- End with one closing line that reads like an epitaph or a blessing
  for the codebase.
- Output ONLY the story. No title, no preamble, no commentary.

Commit history (most recent first):
{commit_block}
"""


def generate_story(
    repo_path: str,
    model: str = "gemma3:4b",
    limit: int = 40,
    repo_name: Optional[str] = None,
    host: str = "http://localhost:11434",
) -> tuple[str, List[Commit]]:
    """Pull the git log, build the prompt, and ask the local model for a story.

    Returns (story_text, commits) so the UI can show both the narrative
    and the raw history it was built from.
    """
    if ollama is None:
        raise GhostLogError(
            "The 'ollama' Python package isn't installed. "
            "Run: pip install ollama"
        )

    commits = get_commit_log(repo_path, limit=limit)
    name = repo_name or repo_path.rstrip("/\\").split("/")[-1].split("\\")[-1]
    prompt = build_prompt(commits, name)

    client = ollama.Client(host=host)
    try:
        response = client.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:  # ollama raises its own ResponseError, connection errors, etc.
        raise GhostLogError(
            "Couldn't reach Ollama. Is it running? Try `ollama serve` "
            f"in another terminal, and make sure you've pulled the model "
            f"with `ollama pull {model}`.\n\nDetails: {exc}"
        ) from exc

    return response["message"]["content"].strip(), commits
