from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd

class IDatabaseConnection(ABC):
    """Interface para conexión a base de datos"""
    
    @abstractmethod
    def connect(self) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def execute_query_dataframe(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        pass

class IAuthService(ABC):
    """Interface para servicio de autenticación"""
    
    @abstractmethod
    def validate_request_hash(self, request_data: str, provided_hash: str) -> bool:
        pass
    
    @abstractmethod
    def generate_hash(self, data: str) -> str:
        pass

class IDataAnalysisService(ABC):
    """Interface para servicio de análisis de datos"""
    
    @abstractmethod
    def analyze_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_summary_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        pass