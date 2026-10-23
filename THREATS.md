# THREATS.md

| # | Threat | What I did | Status |
|---|--------|------------|--------|
| 1 | Guessing document ids (/documents/2) | Every route calls get_doc -> can(); strangers get 403 and a log entry | Closed, tested |
| 2 | Hiding buttons only | Server checks every request, not just the page | Closed, tested |
| 3 | Revoked user keeps access | No cached permissions or links; the grant row is deleted and checked each request | Closed, tested |
| 4 | Direct file URL | Files are stored outside static/ under random names, served only by the download route | Closed |
| 5 | Uploading bad files | Extension allow-list, 4 MB limit, empty files refused, safe file names | Partly closed |
| 6 | Search leaking documents | Search starts from documents the user may see | Closed, tested |
| 7 | Editing the audit log | App never updates/deletes; DB triggers block it | Partly closed |
| 8 | Fake logins / role changes | Role read from the database each request; passwords hashed | Closed |
| 9 | CSRF | CSRF tokens on every form | Closed |
| 10 | Admin reading files | Admin can delete but cannot read contents | Closed, tested |

## Accepted risks (known, not fixed)
- File content is not checked, only the extension (a renamed .exe as .pdf passes).
- Someone with direct database access could drop the triggers and edit the log.
- No rate limit on login attempts.
- Guessable numeric document ids (access is still checked every time).
- Refused access returns 403, so outsiders can tell a document exists.
- Deleting a document is permanent; there is no recovery or version history.
- No sharing with people outside the company; no AI suggestion feature.
- Uploaded files are not encrypted on disk.