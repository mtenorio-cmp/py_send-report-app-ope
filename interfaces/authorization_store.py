from abc import ABC, abstractmethod

class IAuthorizationStore(ABC):
    @abstractmethod
    def add_user(self, user_id: int): pass

    @abstractmethod
    def remove_user(self, user_id: int): pass

    @abstractmethod
    def is_authorized(self, user_id: int) -> bool: pass
