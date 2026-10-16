"""Parse a small local allowlist; model or comment text is never executed."""
import re

from .registry import dispatch

INTENT_EXAMPLES = [
    "listar artículos publicados",
    "ver comentarios del artículo 1",
    "borrar comentarios del artículo 5",
    "ejecutar SQL para borrar todos los artículos",
]


def execute_intent(intent, approve=None):
    if not isinstance(intent, str):
        return {"status": "denied", "reason": "invalid_intent"}
    text = intent.strip().casefold()
    if text == "listar artículos publicados":
        return dispatch("list_posts", approve=approve)
    match = re.fullmatch(r"(ver|borrar) comentarios del artículo ([1-9][0-9]*)", text)
    if match:
        action = "comments_of_post" if match[1] == "ver" else "delete_comments"
        return dispatch(action, {"article_id": int(match[2])}, approve=approve)
    return {"status": "denied", "reason": "intent_not_allowed"}
