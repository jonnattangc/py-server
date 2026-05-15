from app.domain.entities import Bank, Deposit, OtpEntry, User


class TestEntities:
    def test_bank_creation(self):
        bank = Bank(id=1, account="123", name="Test Bank")
        assert bank.id == 1
        assert bank.account == "123"
        assert bank.name == "Test Bank"

    def test_deposit_defaults(self):
        dep = Deposit()
        assert dep.origin_bank is None
        assert dep.amount is None

    def test_deposit_with_values(self):
        dep = Deposit(origin_bank="Banco", amount=1000)
        assert dep.origin_bank == "Banco"
        assert dep.amount == 1000

    def test_otp_entry_creation(self):
        otp = OtpEntry(reference="ref-1", otp_hash="hash", channel="sms")
        assert otp.reference == "ref-1"
        assert otp.status == "PENDING"

    def test_user_creation(self):
        user = User(name="Jonnattan", mobile="+569")
        assert user.name == "Jonnattan"
        assert user.state is None
