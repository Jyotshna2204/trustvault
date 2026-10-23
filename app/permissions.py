from .models import Grant


def can(user, doc, action):
    """Return True only if this user may do this action. Default is NO."""
    if not user.is_authenticated or doc is None:
        return False
    if doc.owner_id == user.id:          # owner can do everything
        return True
    if action == "delete" and user.role == "admin":
        return True                      # admin can delete but not read
    if action in ("read", "edit"):
        grant = Grant.query.filter_by(document_id=doc.id, user_id=user.id).first()
        if grant is None:
            return False
        return action == "read" or grant.level == "edit"
    return False                         # "share" and anything else: owner only