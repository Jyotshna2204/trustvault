# TrustVault

Secure document sharing with an audit trail. Built with Python, Flask, SQLite.

## Roles
- **Admin:** manages everything, sees the audit log, can delete a document, cannot read its contents.
- **Owner:** uploads documents, grants and revokes read/edit access.
- **Viewer:** sees only documents shared with them.

## Run locally
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    copy .env.example .env      (then set SECRET_KEY)
    python seed.py              (prints demo passwords)
    python run.py
    python -m pytest -q

## Demo accounts
(Added after deployment.)

## Not built / unfinished
See THREATS.md (accepted risks).