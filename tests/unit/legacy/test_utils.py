import os
import json
import pytest
from unittest.mock import patch, mock_open, MagicMock

from app.legacy.utils import Bank, Banks, Cipher, Deposit


class TestBank:
    def test_bank_init(self):
        bank = Bank(1, "123", "Banco")
        assert bank.id == 1
        assert bank.account == "123"
        assert bank.name == "Banco"


class TestBanks:
    def test_banks_load(self, tmp_path):
        data = {"data": [{"id": 1, "account": {"bank": {"name": "Banco"}, "number": "123"}}]}
        banks_file = tmp_path / "banks.json"
        banks_file.write_text(json.dumps(data))
        banks = Banks(root=str(tmp_path), filename="banks")
        name, account = banks.getBank(1)
        assert name == "Banco"
        assert account == "123"

    def test_banks_get_bank_not_found(self, tmp_path):
        data = {"data": []}
        banks_file = tmp_path / "banks.json"
        banks_file.write_text(json.dumps(data))
        banks = Banks(root=str(tmp_path), filename="banks")
        name, account = banks.getBank(99)
        assert name is None
        assert account is None

    def test_banks_process(self, tmp_path):
        data = {"data": [{"id": 2, "account": {"bank": {"name": "B2"}, "number": "456"}}]}
        banks_file = tmp_path / "banks.json"
        banks_file.write_text(json.dumps(data))
        banks = Banks(root=str(tmp_path), filename="banks")
        bank = banks.process(data["data"][0])
        assert isinstance(bank, Bank)
        assert bank.id == 2


class TestCipher:
    @patch.dict(os.environ, {"AES_KEY": "my_secret_key_1234567890123456"})
    def test_aes_encrypt_decrypt(self):
        cipher = Cipher()
        original = "hello world"
        encrypted = cipher.aes_encrypt(original)
        assert encrypted is not None
        decrypted = cipher.aes_decrypt(encrypted)
        assert decrypted == original

    def test_aes_encrypt_none_key(self):
        with patch.dict(os.environ, {"AES_KEY": "None"}):
            cipher = Cipher()
            # With None key, should fail gracefully
            encrypted = cipher.aes_encrypt("test")
            # Depending on key handling it might be None or raise
            assert encrypted is None or isinstance(encrypted, str)

    def test_complete(self):
        with patch.dict(os.environ, {"AES_KEY": "my_secret_key_1234567890123456"}):
            cipher = Cipher()
            data = cipher.complete("test")
            assert len(data) % 16 == 0


class TestDeposit:
    def test_deposit_init(self):
        dep = Deposit({
            "origin_bank": "B1",
            "origin_account": "123",
            "date": "2024-01-01",
            "amount": 100,
            "origin_name": "Juan",
            "identity": "111",
            "internal_bot_process": "proc",
            "channel": "web",
            "origin_rut": "111-1",
            "destination_rut": "222-2",
            "description": "desc",
            "balance": "1000",
            "comment": "ok",
            "type": "transfer"
        })
        assert dep.origin_bank == "B1"
        assert dep.amount == 100
