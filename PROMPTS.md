# PROMPTS.md

I used an AI assistant (Claude) throughout this project. It helped me analyse
the problem statement, plan the architecture, and write code one small stage
at a time. I did not paste code blindly. For each stage I read the code, asked
for explanations of parts I did not understand, ran it, tested it, and fixed
what broke.

## How I worked with the AI

- I asked it to explain the problem and make a plan before writing any code.
- I chose a small system with a strong permission model, because time was short.
- I built in small stages and ran and tested each one before moving on.
- I treat the AI's authorisation and audit-log code as the highest risk, so I
  test those parts myself and record every mistake I find below.

## Entries

(Dated entries are added here when I find real mistakes or problems. Each one
records what I asked, what the AI produced, what was wrong, and what I did
instead, with a commit link.)
### real secret key committed in .env.example
- **What happened:** while creating .env.example I put my real SECRET_KEY in it,
  and it was committed and pushed.
- **How it was caught:** I compared file sizes in `dir -Force` (.env and
  .env.example were the same size) and then checked with `git show HEAD:.env.example`.
- **What was wrong:** the real key was in Git history.
- **What I did:** replaced the file with a placeholder, generated and set a new
  key in .env (the old one is treated as exposed), and now add files by name
  instead of `git add .`. Commit:.env.example
### Entry 3 : hash chain too complex
- Asked AI for an audit log. It produced a hash chain I could not explain.
- Did: asked for a simpler version, kept only append-only DB triggers.
  Commit: <link>

### Entry 4 : authorisation - permission check missing from get_doc
- Asked: for a document permission check.
- Wrong: my test run showed 5 tests failing (strangers got 200, a revoked
  user could still download, admin could download, denied was not logged).
  The get_doc function was missing `not can(...)`.
- Did: restored the check. 22 tests pass. I also removed the check on purpose
  (mutation test) and 5 tests failed, so the tests really test authorisation.
  Note: the broken version was committed once. Fix commit: <link>

### Entry 5 : setup order bugs in app/__init__.py
- Wrong: the instructions put UPLOAD_FOLDER and register_blueprint(docs) in
  the wrong order, giving KeyError and UnboundLocalError.
- Did: rewrote __init__.py in the correct order. Commit: <link>

### Entry 6 : audit/auth - search variable mix-up and missing templates
- Wrong: search code used `items` and `query` inconsistently
  (UnboundLocalError); templates were missing (TemplateNotFound).
- Did: fixed both, tests caught the first. Commit: <link>
### Entry 7: Register route used db without importing it
- Problem: the register code I was given used `db` but auth.py never imported it.
  The new register test failed with NameError.
- Fix: added `from .extensions import db`. All 23 tests pass.