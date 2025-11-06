# Research

This repository is for asynchronous code research projects using Claude Code and other coding agents.

## How it works

The `claude.md` file in the root of this repository points to `agents.md`, which contains instructions for coding agents on how to organize their research work.

When you give Claude Code a research task, it will:

1. Create a new folder for the investigation
2. Track its progress in a `notes.md` file
3. Write any code needed for the research
4. Summarize findings in a `README.md`
5. Commit the results

## Usage

Simply ask Claude Code to research something, and it will create a fresh directory following the structure defined in `agents.md`.

Each research project gets its own folder with:
- `notes.md` - Investigation notes and learnings
- `README.md` - Summary of findings
- Any code written or diffs generated
- Relevant binary files under 2MB

## Inspiration

This setup is inspired by [Simon Willison's async code research approach](https://simonwillison.net/2025/Nov/6/async-code-research/).
