import pytest
import pandas as pd
from datetime import date
from typing import List, Dict, Any, Optional, Generator
from services.documento_query_service import DocumentoQueryService
from interfaces.database_interface import IDatabaseConnection
import pymysql

class MockDatabaseConnection(IDatabaseConnection):
    def connect(self) -> bool:
        return True
    
    def disconnect(self) -> None:
        pass
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        return []
    
    def execute_query_dataframe(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        return pd.DataFrame()
    
    def get_cursor(self, query: str, params: Optional[Dict] = None):
        yield None

class TestDocumentoQueryService:
    @pytest.fixture
    def db_connection(self):
        return MockDatabaseConnection()

    @pytest.fixture
    def service(self, db_connection):
        return DocumentoQueryService(db_connection)

    def test_service_initialization(self, service):
        assert isinstance(service, DocumentoQueryService)

    def test_get_delivery_documents_by_date_range(self, service):
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        result = service.get_delivery_documents_by_date_range(start_date, end_date)
        assert isinstance(result, pd.DataFrame)

    def test_build_where_with_empty_filters(self, service):
        where_clauses, params = service._build_where([], {})
        assert where_clauses == []
        assert params == {}

    def test_build_where_with_in_filter(self, service):
        filters = {"doc_mot__in": ["VENTA", "TRASLADO"]}
        where_clauses, params = service._build_where([], filters)
        assert len(where_clauses) == 1
        assert "IN" in where_clauses[0]
        assert len(params) == 2

    def test_query_documents_with_conditions(self, service):
        conditions = {
            "doc_mot__in": ["VENTA"],
            "v.placa__like": "%ABC%"
        }
        result = service.query_documents(conditions)
        assert isinstance(result, pd.DataFrame)