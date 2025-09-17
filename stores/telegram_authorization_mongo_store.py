import logging
from typing import List, Dict, Any, Optional
from interfaces.telegram_authorization_store import ITelegramAuthorizationStore
from pymongo import MongoClient
from datetime import datetime

logger = logging.getLogger(__name__)


class TelegramAuthorizationMongoStore(ITelegramAuthorizationStore):
    """
    Store para manejar usuarios autorizados en MongoDB.
    Implementa Singleton + Inyección de Dependencias.
    """

    _instance: Optional["TelegramAuthorizationMongoStore"] = None
    _collection_name = "telegram_authorized_users"

    def __new__(cls, mongo_client: MongoClient, db_name: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, mongo_client: MongoClient, db_name: str):
        if not hasattr(self, "_initialized"):  # evita re-inicializar en singleton
            self.client = mongo_client
            self.db = self.client[db_name]
            self.collection = self.db[self._collection_name]
            self.collection.create_index("user_id", unique=True)  # índice único
            self._initialized = True
            logger.info(f"✅ Colección `{self._collection_name}` lista en MongoDB")

    def add_user(self, user_id: int, username: str = None) -> None:
        try:
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"username": username, "created_at": datetime.utcnow()}},
                upsert=True,
            )
            logger.info(f"🎉 Usuario {user_id} ({username}) autorizado en MongoDB")
        except Exception as e:
            logger.error(f"❌ Error agregando usuario en MongoDB: {e}")
            raise

    def remove_user(self, user_id: int) -> None:
        try:
            self.collection.delete_one({"user_id": user_id})
            logger.info(f"🗑️ Usuario {user_id} eliminado de MongoDB")
        except Exception as e:
            logger.error(f"❌ Error eliminando usuario {user_id}: {e}")
            raise

    def is_authorized(self, user_id: int) -> bool:
        try:
            return self.collection.find_one({"user_id": user_id}) is not None
        except Exception as e:
            logger.error(f"❌ Error verificando usuario {user_id} en MongoDB: {e}")
            return False

    def list_users(self) -> List[Dict[str, Any]]:
        try:
            users = list(
                self.collection.find({}, {"_id": 0, "user_id": 1, "username": 1, "created_at": 1})
                .sort("created_at", -1)
            )
            return users
        except Exception as e:
            logger.error(f"❌ Error listando usuarios en MongoDB: {e}")
            return []
