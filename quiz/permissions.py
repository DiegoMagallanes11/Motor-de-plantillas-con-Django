from rest_framework.permissions import BasePermission

AGENT_GROUP = "agente"


class AgentPermission(BasePermission):
    """Who may do what. This is the SERVER's rule: it holds even if a client misbehaves.

    The rule the lab asks for:
      - a person (user with is_staff) can do anything;
      - a member of the group «agente» can read, create and modify, but NEVER delete;
      - anybody else who is logged in can only read;
      - an unknown method is denied (deny by default).

    Implemented for Lab 08. Agent-group membership takes priority over staff
    membership, so an agent never gains deletion rights through a second role.
    """

    def has_permission(self, request, view):
        if request.method not in {"GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"}:
            return False
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.groups.filter(name=AGENT_GROUP).exists():
            return request.method != "DELETE"
        if user.is_staff:
            return True
        return request.method in {"GET", "HEAD", "OPTIONS"}
