"""Domain interface definitions (ports)."""

from abc import ABC, abstractmethod
from typing import Optional


class IDatabaseConnection(ABC):
    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def is_connected(self) -> bool: ...

    @abstractmethod
    def close(self) -> None: ...

    @property
    @abstractmethod
    def raw(self): ...


class IUserRepository(ABC):
    @abstractmethod
    def verify_credentials(self, username: str, password: str) -> Optional[str]: ...

    @abstractmethod
    def create_user(self, username: str, password_hash: str) -> None: ...


class IOtpRepository(ABC):
    @abstractmethod
    def create(self, otp_data) -> None: ...

    @abstractmethod
    def find_pending_by_channel(self, channel: str): ...

    @abstractmethod
    def find_by_reference(self, reference: str): ...

    @abstractmethod
    def burn(self, reference: str, status: str, attempt: int) -> None: ...
