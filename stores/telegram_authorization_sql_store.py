import logging
from typing import List, Dict, Any, Optional
from interfaces.telegram_authorization_store import ITelegramAuthorizationStore
from database.mariadb_connection import MariaDBConnection

logger = logging.getLogger(__name__)


class TelegramAuthorizationSqlStore(ITelegramAuthorizationStore):
    """
    Store para manejar usuarios autorizados de Telegram en DB.
    Implementa Singleton + Inyección de Dependencias.
    """

    _instance: Optional["TelegramAuthorizationSqlStore"] = None
    _name_table = "telegram_authorized_users"

    def __new__(cls, db: MariaDBConnection):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db: MariaDBConnection):
        if not hasattr(self, "_initialized"):  # evita re-inicializar en el singleton
            self.db = db
            self._ensure_table_exists()
            self._initialized = True

    def _ensure_table_exists(self):
        """Crea la tabla si no existe"""
        query = f"""
        CREATE TABLE IF NOT EXISTS {self._name_table} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT UNIQUE NOT NULL,
            username VARCHAR(100) NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query)
            logger.info(f"✅ Tabla `{self._name_table}` verificada/creada correctamente")
        except Exception as e:
            logger.error(f"❌ Error creando/verificando tabla {self._name_table}: {e}")
            raise

    def add_user(self, user_id: int, username: str = None) -> None:
        """Agrega un usuario autorizado"""
        query = f"""
        INSERT INTO {self._name_table} (user_id, username)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE username = VALUES(username)
        """
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (user_id, username))
            logger.info(f"🎉 Usuario {user_id} ({username}) autorizado")
        except Exception as e:
            logger.error(f"❌ Error agregando usuario autorizado {user_id}: {e}")
            raise

    def remove_user(self, user_id: int) -> None:
        """Elimina un usuario autorizado"""
        query = f"DELETE FROM {self._name_table} WHERE user_id = %s"
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (user_id,))
            logger.info(f"🗑️ Usuario {user_id} eliminado de autorizados")
        except Exception as e:
            logger.error(f"❌ Error eliminando usuario {user_id}: {e}")
            raise

    def is_authorized(self, user_id: int) -> bool:
        """Verifica si un usuario está autorizado"""
        query = f"SELECT 1 FROM {self._name_table} WHERE user_id = %s LIMIT 1"
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"❌ Error verificando usuario {user_id}: {e}")
            return False

    def list_users(self) -> List[Dict[str, Any]]:
        """Devuelve todos los usuarios autorizados"""
        query = f"""
        SELECT user_id, username, created_at 
        FROM {self._name_table} 
        ORDER BY created_at DESC
        """
        try:
            return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"❌ Error listando usuarios autorizados: {e}")
            return []
