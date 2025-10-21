import pytest
from models.guia_model import GuiaUpdateRequest
from datetime import date

class TestGuiaUpdateRequest:
    @pytest.fixture
    def guia_request(self):
        return GuiaUpdateRequest(
            fact_serie="F001",
            fact_num=12345,
            guia_serie="G001",
            guia_num=54321,
            guia_fecha=date.today(),
            guia_program_fecha=date.today(),
            guia_agencia="AGENCIA_TEST"
        )

    def test_guia_request_initialization(self, guia_request):
        assert isinstance(guia_request, GuiaUpdateRequest)
        assert guia_request.fact_serie == "F001"
        assert guia_request.fact_num == 12345
        assert guia_request.guia_serie == "G001"
        assert guia_request.guia_num == 54321
        assert isinstance(guia_request.guia_fecha, date)
        assert isinstance(guia_request.guia_program_fecha, date)
        assert guia_request.guia_agencia == "AGENCIA_TEST"