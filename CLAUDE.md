# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a public GitHub-connected project for developing and sharing Claude Code skills. Skills are custom workflow automations that extend Claude Code's capabilities.

## Repository Structure

- Skills are defined and organized here for version control and public sharing.
- The repository connects to a public GitHub remote for open development and distribution.

## Common Commands

Since this project is skill-focused, there is no traditional build/test pipeline. Key operations include:

- `git status` — check current changes before committing skill updates.
- `git add <file>` and `git commit -m "..."` — stage and commit skill changes.
- `git push` — publish updates to the public GitHub repository.

## Skill Development Notes

- Each skill should be self-contained and documented.
- Follow the Claude Code skill schema when defining new skills.
- Keep skills focused on a single workflow or automation target.
- When modifying skills, verify syntax and test logic before committing.

## Git Workflow

- This repo is public; do not commit sensitive data (tokens, keys, private configs).
- Use clear commit messages describing skill changes or additions.
