| Route | Method | Who may call it |
|-------|--------|-----------------|
| /login | GET, POST | anyone |
| /logout | POST | logged in |
| /dashboard | GET | logged in |
| /admin, /admin/audit | GET | admin |
| /documents/ | GET | logged in (own or shared documents only) |
| /documents/upload | GET, POST | owner |
| /documents/<id> | GET | owner, or a user with a grant |
| /documents/<id>/download | GET | owner, or a user with a grant |
| /documents/<id>/edit | POST | owner, or a user with an edit grant |
| /documents/<id>/delete | POST | owner or admin |
| /documents/<id>/grant | POST | owner |
| /documents/<id>/revoke/<user> | POST | owner |