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