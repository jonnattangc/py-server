import pytest
from app.domain.interfaces import (
    IDatabaseConnection,
    IUserRepository,
    IOtpRepository,
    IExternalHttpClient,
    IAwsService,
    IWazaService,
)


class TestInterfaces:
    def test_idatabase_connection_is_abstract(self):
        with pytest.raises(TypeError):
            IDatabaseConnection()

    def test_iuser_repository_is_abstract(self):
        with pytest.raises(TypeError):
            IUserRepository()

    def test_iotp_repository_is_abstract(self):
        with pytest.raises(TypeError):
            IOtpRepository()

    def test_iexternal_http_client_is_abstract(self):
        with pytest.raises(TypeError):
            IExternalHttpClient()

    def test_iaws_service_is_abstract(self):
        with pytest.raises(TypeError):
            IAwsService()

    def test_iwaza_service_is_abstract(self):
        with pytest.raises(TypeError):
            IWazaService()
