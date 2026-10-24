# THREATS.md

## Problems I thought of and what I did
1. Guessing a document number in the URL: every document route calls get_doc(),
   which calls can(). Strangers get 403 and the attempt is logged. (tested)
2. Only hiding buttons: the server checks every request. (tested)
3. A removed user keeps access: the grant is deleted and checked on every
   request, so access ends at once. (tested)
4. Opening the file directly: files are saved under random names outside the
   static folder and only sent by the download route.
5. Bad uploads: only pdf, txt, png, jpg, jpeg, docx; max 4 MB; empty files
   refused; file names cleaned. (tested)
6. Search showing other people's documents: search only looks inside documents
   the user is allowed to see. (tested)
7. Changing the audit log: the app never edits or deletes it, and database
   triggers block it.
8. Pretending to be admin: the role is read from the database on every request.
   Passwords are hashed.
9. Fake form submissions (CSRF): every form has a CSRF token.
10. Admin reading files: the admin can delete a document but cannot read it. (tested)

## Known weak points (not fixed)
- Files are checked by extension only, not by content.
- Someone with direct access to the database file could remove the triggers.
- No limit on login attempts.
- Document ids are simple numbers (access is still checked every time).
- A refused request returns 403, so a user can tell a document exists.
- Deleting a document is permanent. No versions or recovery.
- No sharing with people outside the system. No AI suggestion feature.
- Files are not encrypted on disk.
- On the free host, uploaded files and the database can disappear when the
  server restarts.
  - The register page lets anyone create a viewer account (no email check).
- No limit on how many failed logins or junk audit entries someone can create.
- Search by title uses the text typed by the user in a database query
  (it is parameterised, so it is not SQL injection, but I did not test odd input).