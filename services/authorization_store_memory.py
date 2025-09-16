from interfaces.authorization_store import IAuthorizationStore

class InMemoryAuthorizationStore(IAuthorizationStore):
    def __init__(self):
        self._authorized_users = set()

    def add_user(self, user_id: int):
        self._authorized_users.add(user_id)

    def remove_user(self, user_id: int):
        self._authorized_users.discard(user_id)

    def is_authorized(self, user_id: int) -> bool:
        return user_id in self._authorized_users
