import pytest
from unittest.mock import patch, MagicMock

from app.legacy.utilwaza import UtilWaza


class TestUtilWazaPureFunctions:
    @patch("app.legacy.utilwaza.pymysql.connect")
    def test_clean_leters(self, mock_connect):
        mock_connect.return_value = MagicMock()
        w = UtilWaza()
        assert w.cleanLeters("abc123") == "123"
        assert w.cleanLeters("12-34.56") == "12-34.56"

    @patch("app.legacy.utilwaza.pymysql.connect")
    def test_clean_numbers(self, mock_connect):
        mock_connect.return_value = MagicMock()
        w = UtilWaza()
        assert w.cleanNumbers("abc123") == "abc"

    @patch("app.legacy.utilwaza.pymysql.connect")
    def test_get_doc_number(self, mock_connect):
        mock_connect.return_value = MagicMock()
        w = UtilWaza()
        assert w.getDocNumber("12.345.678-9") == "12.345.678-9"
        assert w.getDocNumber(None) is None
        assert w.getDocNumber("123456789012345") == "12345678901"

    @patch("app.legacy.utilwaza.pymysql.connect")
    def test_get_nationality(self, mock_connect):
        mock_connect.return_value = MagicMock()
        w = UtilWaza()
        assert w.getNationality("Chilena123") == "Chilena"
        assert w.getNationality(None) is None

    @patch("app.legacy.utilwaza.pymysql.connect")
    def test_get_sex(self, mock_connect):
        mock_connect.return_value = MagicMock()
        w = UtilWaza()
        assert w.getSex("M") == "Masculino"
        assert w.getSex("F") == "Femenino"
        assert w.getSex("X") == "DESCONOCIDO"
        assert w.getSex(None) is None

    @patch("app.legacy.utilwaza.pymysql.connect")
    def test_get_name(self, mock_connect):
        mock_connect.return_value = MagicMock()
        w = UtilWaza()
        assert w.getName("juan perez123") == " Juan Perez"
        assert w.getName(None) is None

    @patch("app.legacy.utilwaza.pymysql.connect")
    def test_get_rut(self, mock_connect):
        mock_connect.return_value = MagicMock()
        w = UtilWaza()
        assert w.getRut("12.345.678-9") == "12345678-9"
        assert w.getRut(None) is None

    @patch("app.legacy.utilwaza.pymysql.connect")
    def test_get_birth_date(self, mock_connect):
        mock_connect.return_value = MagicMock()
        w = UtilWaza()
        assert w.getBirthDate(["1", "2", "1990"]) == "1990/02/01 00:00:00"
        assert w.getBirthDate(None) is None

    @patch("app.legacy.utilwaza.pymysql.connect")
    def test_get_random_action(self, mock_connect):
        mock_connect.return_value = MagicMock()
        w = UtilWaza()
        action, desc = w.getRandomAction()
        assert action in ["face_to_the_left", "face_to_the_right", "close_the_eyes", "smile", "face_from_far_to_near"]
        assert len(desc) > 0

    @patch("app.legacy.utilwaza.pymysql.connect")
    def test_get_next_state(self, mock_connect):
        mock_connect.return_value = MagicMock()
        w = UtilWaza()
        assert w.getNextState(None) == "RECIVING_IMAGE_CI"
        assert w.getNextState("RECIVING_IMAGE_CI") == "RECIVING_IMAGE_FACE"
        assert w.getNextState("RECIVING_IMAGE_FACE") == "RECIVING_IMAGE_ACTION"
        assert w.getNextState("RECIVING_IMAGE_ACTION") == "VALIDATING_IDENTITY"

    @patch("app.legacy.utilwaza.pymysql.connect")
    def test_process_text_message(self, mock_connect):
        mock_connect.return_value = MagicMock()
        w = UtilWaza()
        with patch.object(w, "buildResponse", return_value="Hola"):
            # We need to patch UtilLlm inside the method
            with patch("app.legacy.utilwaza.UtilLlm") as mock_llm:
                mock_inst = MagicMock()
                mock_inst.sendQuestion.return_value = "Respuesta"
                mock_llm.return_value = mock_inst
                resp, code = w.processTextMessage({"mesagge": "Hola"})
                assert code == 200
                assert resp["success"] is True

    @patch("app.legacy.utilwaza.pymysql.connect")
    def test_process_text_message_none(self, mock_connect):
        mock_connect.return_value = MagicMock()
        w = UtilWaza()
        resp, code = w.processTextMessage(None)
        assert resp is None
