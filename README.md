# TrustVault

A small document sharing website with an audit log. Python, Flask, SQLite.

## What it does
- Three roles: admin, owner, viewer.
- Owners upload documents and give or remove read/edit access.
- Only people with access can read or download a document.
- Every upload, download, change, delete, grant, revoke and refused attempt is logged.
- Search by title, category, owner and date.
- Admin page shows the audit log.

## Roles
- Admin: sees the audit log, can delete a document, cannot read it.
- Owner: uploads documents and manages access to them.
- Viewer: sees only documents shared with them.

## Permission model (in my words)
Each document has one owner. The owner can give another user "read" or "edit".
One function, can(), decides every request. If there is no grant, the answer is no.

## Run on your computer
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    copy .env.example .env      (then put your own SECRET_KEY in .env)
    python seed.py
    python run.py
    python -m pytest -q

## Live site and demo accounts
Live link: (add after deploying)
- admin@trustvault.test / (password)
- owner1@trustvault.test / (password)
- viewer@trustvault.test / (password)

## How I used AI
I used Claude for planning and writing code in small steps. See PROMPTS.md for
the mistakes I found and fixed.

## Not built / unfinished
See THREATS.md. No external sharing, no versions, no AI suggestion feature.
Uploaded files may disappear on the free host when it restarts.