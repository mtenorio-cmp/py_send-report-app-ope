import hashlib
import hmac
from typing import str
from config import settings
from interfaces.database_interface import IAuthService
import logging

logger = logging.getLogger(__name__)

class AuthService(IAuthService):
    """Servicio de autenticación usando HMAC-SHA256"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY.encode('utf-8')
    
    def generate_hash(self, data: str) -> str:
        """Genera hash HMAC-SHA256 para los datos proporcionados"""
        return hmac.new(
            self.secret_key,
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def validate_request_hash(self, request_data: str, provided_hash: str) -> bool:
        """Valida que el hash proporcionado coincida con los datos de la solicitud"""
        try:
            expected_hash = self.generate_hash(request_data)
            is_valid = hmac.compare_digest(expected_hash, provided_hash)
            
            if is_valid:
                logger.info("Solicitud autorizada correctamente")
            else:
                logger.warning("Intento de acceso con hash inválido")
            
            return is_valid
        except Exception as e:
            logger.error(f"Error validando hash: {e}")
            return False
