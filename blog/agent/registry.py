"""A local teaching registry with explicit actions and state-bound approval.

This is not a remote authorization API. Only trusted local CLI callers may
approve plans. Stored comments are always returned as data, never as actions.
"""
import hashlib
import hmac
import json
import re

from django.conf import settings
from django.db import transaction

from blog.models import Article, Comment

READ_ACTIONS = frozenset({"list_posts", "comments_of_post"})
WRITE_ACTIONS = frozenset({"delete_comments"})


def _denied(reason):
    return {"status": "denied", "reason": reason}


def _valid_article_arguments(arguments):
    return (
        set(arguments) == {"article_id"}
        and type(arguments["article_id"]) is int
        and arguments["article_id"] > 0
    )


def _snapshot(article_id):
    return list(Comment.objects.select_for_update().filter(
        article_id=article_id
    ).order_by("id").values(
        "id", "article_id", "author_name", "body", "is_approved", "updated_at"
    ))


def _plan_hash(article_id, comments):
    payload = json.dumps(
        {"version": 1, "action": "delete_comments", "article_id": article_id,
         "comments": comments},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        default=lambda value: value.isoformat(),
    ).encode("utf-8")
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"), payload, hashlib.sha256
    ).hexdigest()


def dispatch(action, arguments=None, approve=None):
    if not isinstance(action, str) or action not in READ_ACTIONS | WRITE_ACTIONS:
        return _denied("action_not_allowed")
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        return _denied("invalid_arguments")
    if approve is not None and (
        not isinstance(approve, str) or re.fullmatch(r"[0-9a-f]{64}", approve) is None
    ):
        return _denied("invalid_approval")
    if action == "list_posts":
        if arguments or approve is not None:
            return _denied("unexpected_arguments")
        return {"status": "ok", "action": action, "data": list(
            Article.objects.filter(is_published=True).order_by("id").values(
                "id", "title"
            )
        )}
    if not _valid_article_arguments(arguments):
        return _denied("invalid_arguments")
    article_id = arguments["article_id"]
    if not Article.objects.filter(pk=article_id).exists():
        return _denied("article_not_found")
    if action == "comments_of_post":
        if approve is not None:
            return _denied("unexpected_approval")
        return {
            "status": "ok", "action": action, "untrusted_content": True,
            "data": list(Comment.objects.filter(article_id=article_id).values(
                "id", "body", "is_approved"
            )),
        }
    with transaction.atomic():
        comments = _snapshot(article_id)
        signature = _plan_hash(article_id, comments)
        if approve is None:
            return {
                "status": "approval_required", "action": action,
                "article_id": article_id, "comment_ids": [row["id"] for row in comments],
                "count": len(comments), "plan_hash": signature,
            }
        if not hmac.compare_digest(signature, approve):
            return _denied("stale_or_invalid_plan")
        comment_ids = [row["id"] for row in comments]
        removed, _ = Comment.objects.filter(
            article_id=article_id, pk__in=comment_ids
        ).delete()
        if removed != len(comment_ids):
            raise RuntimeError("Comment scope changed; transaction rolled back")
        return {
            "status": "ok", "action": action,
            "article_id": article_id, "deleted": removed,
        }
