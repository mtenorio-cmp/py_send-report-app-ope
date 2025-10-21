import pytest
import pandas as pd
from datetime import date, datetime
from services.data_analysis_service import DataAnalysisService

class TestDataAnalysisService:
    @pytest.fixture
    def service(self):
        return DataAnalysisService()
    
    @pytest.fixture
    def sample_data(self):
        return pd.DataFrame({
            'rd_hora_sal': ['2025-10-21 10:00:00', '2025-10-21 11:00:00'],
            'doc_fec_crea': ['2025-10-21 08:00:00', '2025-10-21 09:00:00'],
            'doc_con_pag': ['Contado contra entrega;24', 'PADEL;24'],
            'doc_peso_tot': [100.0, 200.0],
            'doc_cant_bult': [10, 20],
            'veh_placa': ['ABC123', 'XYZ789'],
            'chofer_nom_comp': ['Chofer 1', 'Chofer 2'],
            'doc_num_fac': ['F001-001', 'F001-002'],
            'doc_raz_soc': ['Cliente 1', 'Cliente 2'],
            'rut_fec_ini': [True, False],
        })

    def test_service_initialization(self, service):
        assert isinstance(service, DataAnalysisService)

    def test_get_promedio_tiempo_despacho(self, service, sample_data):
        result = service.get_promedio_tiempo_despacho(sample_data)
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(item, dict) for item in result)

    def test_despachados_del_dia_detallado(self, service, sample_data, tmp_path):
        ruta_salida = str(tmp_path / "test_report.png")
        result = service.despachados_del_dia_detallado(
            sample_data,
            date(2025, 10, 21),
            ruta_salida
        )
        assert isinstance(result, str)
        assert result.endswith('.png')