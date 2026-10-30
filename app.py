"""
GhostLog -- The Repo That Talks to the Dead
Hacktoberfest 2026 Week 4: "Ghost in the Machine"

A Streamlit app that reads a local git repository's commit history and
asks a locally-running open-weight model (Gemma, via Ollama) to turn it
into a short Dia de los Muertos-style ghost story. Everything runs on
your machine -- no commit messages, code, or author names ever leave it.
"""

import streamlit as st

from ghost_story import GhostLogError, generate_story

st.set_page_config(
    page_title="GhostLog",
    page_icon="👻",
    layout="centered",
)

st.sidebar.checkbox("Dark theme", value=True, key="dark_mode")

# Determine colors based on dark mode
if st.session_state.dark_mode:
    app_bg = "#0d1117"
    story_bg = "#161b22"
    border_color = "#f0883e"
    text_color = "#e6edf3"
else:
    app_bg = "#f5f5f5"
    story_bg = "#ffffff"
    border_color = "#333333"
    text_color = "#222222"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {app_bg}; }}
    .ghost-story {{
        background: {story_bg};
        border: 2px solid {border_color};
        border-radius: 12px;
        padding: 1.5rem 2rem;
        font-family: Georgia, 'Times New Roman', serif;
        font-size: 1.05rem;
        line-height: 1.7;
        color: {text_color};
        white-space: pre-wrap;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
        position: relative;
    }}
    .ghost-story::after {{
        content: "⚱️";
        position: absolute;
        top: -1.2rem;
        right: 1rem;
        font-size: 2rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("👻 GhostLog")
st.caption("The repo that talks to the dead — Hacktoberfest 2026, Week 4: Ghost in the Machine")

st.write(
    "Point GhostLog at any local git repository. It reads the commit "
    "history, finds the commits made during the **witching hour** "
    "(midnight–4am), and asks a locally-running open-weight model to "
    "weave the history into a short ghost story — in the spirit of "
    "Día de los Muertos."
)

with st.sidebar:
    st.header("Settings")
    model = st.text_input(
        "Ollama model",
        value="gemma3:4b",
        help="Must already be pulled, e.g. `ollama pull gemma3:4b`",
    )
    limit = st.slider("How many recent commits to read", 5, 100, 40)
    host = st.text_input("Ollama host", value="http://localhost:11434")
    st.caption(
        "Runs 100% locally via [Ollama](https://ollama.com). "
        "Nothing about your repo is sent to any external API."
    )

repo_path = st.text_input(
    "Path to a local git repository",
    placeholder="/path/to/your/repo  (or just . for the current folder)",
)

go = st.button("🕯️ Summon the Ghosts", type="primary", use_container_width=True)

if go:
    if not repo_path.strip():
        st.warning("Enter a path to a git repository first.")
    else:
        with st.spinner("Awakening the spirits of your commits..."):
            try:
                story, commits = generate_story(
                    repo_path.strip(), model=model, limit=limit, host=host
                )
            except GhostLogError as e:
                st.error(str(e))
            else:
                witching = [c for c in commits if c.is_witching_hour]

                col1, col2 = st.columns(2)
                col1.metric("Commits read", len(commits))
                col2.metric("Witching-hour commits", len(witching))

                st.markdown(f'<div class="ghost-story">{story}</div>', unsafe_allow_html=True)

                st.download_button(
                    "📜 Download story as Markdown",
                    data=story,
                    file_name="ghost_story.md",
                    mime="text/markdown",
                )

                with st.expander("Show the commits it read"):
                    for c in commits:
                        tag = " 🕯️" if c.is_witching_hour else ""
                        st.text(
                            f"{c.date.strftime('%Y-%m-%d %H:%M')}  "
                            f"{c.author:<20} {c.message}{tag}"
                        )

st.divider()
st.caption(
    "Built for the Hacktoberfest Open-Source AI Challenge: Week 4 — "
    "Ghost in the Machine. Model: open-weight Gemma, run locally via Ollama."
)
