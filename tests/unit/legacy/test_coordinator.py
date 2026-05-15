import pytest
from unittest.mock import patch, MagicMock

from app.legacy.coordinator import Coordinator, Deposit


class TestCoordinator:
    def test_init(self):
        with patch.dict("os.environ", {"TRANSBOT_ID": "99"}):
            coord = Coordinator()
            assert coord.transbot_id == 99

    def test_get_evaluate_dates_no_bank(self):
        with patch.dict("os.environ", {"TRANSBOT_ID": "1"}):
            coord = Coordinator()
            data = coord.getEvaluateDates(-1)
            assert data["status"] == "success"
            assert "deposits" in data

    @patch("app.legacy.coordinator.Banks")
    def test_get_evaluate_dates_with_bank(self, mock_banks_cls):
        mock_banks = MagicMock()
        mock_banks.getBank.return_value = ("Banco", "123")
        mock_banks_cls.return_value = mock_banks
        with patch.dict("os.environ", {"TRANSBOT_ID": "1"}):
            coord = Coordinator()
            # Patch DB cursor inside getEvaluateDates
            coord.db = MagicMock()
            cursor = MagicMock()
            cursor.fetchall.return_value = [{"date": "2024-01-01 10:00:00"}]
            coord.db.cursor.return_value = cursor
            data = coord.getEvaluateDates(1)
            assert data["status"] == "success"
            assert "from_date" in data["deposits"]

    def test_proccess_solicitude_ping(self):
        with patch.dict("os.environ", {"TRANSBOT_ID": "1"}):
            coord = Coordinator()
            class FakeReq:
                args = {}
                method = "GET"
            data, code = coord.proccess_solicitude(FakeReq(), "cmkt/ping")
            assert code == 200
            assert data == {}

    def test_deposit_process(self):
        dep = Deposit({
            "origin_bank": "B1", "origin_account": "123", "date": "2024-01-01",
            "amount": 100, "origin_name": "Juan", "identity": "111",
            "internal_bot_process": "p", "channel": "web", "origin_rut": "1-1",
            "destination_rut": "2-2", "description": "d", "balance": "1000",
            "comment": "ok", "type": "t"
        })
        assert dep.origin_bank == "B1"
