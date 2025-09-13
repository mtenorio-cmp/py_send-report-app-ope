import pymysql
import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from config import settings
from interfaces.database_interface import IDatabaseConnection

logger = logging.getLogger(__name__)


class MariaDBConnection(IDatabaseConnection):
    """Implementación concreta para conexión a MariaDB"""

    def __init__(self):
 
        self.connection = None
        self.connection_config = {
            "host": settings.DB_HOST or "127.0.0.1",
            "port": settings.DB_PORT or 3306,
            "database": settings.DB_NAME,
            "user": settings.DB_USER,
            "password": settings.DB_PASSWORD,
            "charset": "utf8mb4",
            "autocommit": True,
        }

    def connect(self) -> bool:
        """Establece conexión con MariaDB"""
        try:
            if self.connection and self.connection.open:
                return True
            self.connection = pymysql.connect(**self.connection_config)
            logger.info("✅ Conexión a MariaDB establecida exitosamente")
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando a MariaDB: {e}")
            return False

    def disconnect(self) -> None:
        """Cierra la conexión a MariaDB"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("🔌 Conexión a MariaDB cerrada")

    @contextmanager
    def get_cursor(self):
        """Context manager para manejo seguro de cursores"""
        if not self.connection or not self.connection.open:
            if not self.connect():
                raise ConnectionError(
                    "No se pudo establecer conexión a la base de datos"
                )

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        try:
            yield cursor
        finally:
            cursor.close()

    def execute_query(
        self, query: str, params: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """Ejecuta query y retorna resultados como lista de diccionarios"""
        try:
            with self.get_cursor() as cursor:
          
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                logger.info(
                    f"📊 Query ejecutada exitosamente. Filas retornadas: {len(results)}"
                )
                return results
        except Exception as e:
            logger.error(f"🛑 Error ejecutando query: {e}")
            raise

    def execute_query_dataframe(
        self, query: str, params: Optional[List[Any]] = None
    ) -> pd.DataFrame:
        """Ejecuta query y retorna resultados como DataFrame de pandas"""
        try:
            
            if not self.connection or not self.connection.open:
                if not self.connect():
                    raise ConnectionError(
                        "No se pudo establecer conexión a la base de datos"
                    )

            df = pd.read_sql(query, self.connection, params=params or ())
            logger.info(f"✅ DataFrame creado exitosamente. Shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"🛑 Error creando DataFrame: {e}")
            raise
