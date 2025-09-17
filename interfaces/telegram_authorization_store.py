from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ITelegramAuthorizationStore(ABC):
    @abstractmethod
    def add_user(self, user_id: int, username: str = None): pass

    @abstractmethod
    def remove_user(self, user_id: int): pass

    @abstractmethod
    def is_authorized(self, user_id: int) -> bool: pass
    
    @abstractmethod
    def list_users(self) ->  List[Dict[str, Any]]: pass
