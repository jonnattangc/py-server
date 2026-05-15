"""Security / Auth infrastructure."""

from app.infrastructure.persistence.mysql_repositories import UserRepository, MySqlConnection


class BasicAuthProvider:
    """Wraps user verification for Flask-HTTPAuth."""

    def __init__(self):
        db = MySqlConnection()
        db.connect()
        self._repo = UserRepository(db)

    def verify(self, username: str, password: str):
        return self._repo.verify_credentials(username, password)
