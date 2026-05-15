"""Concrete MySQL persistence implementations."""

import logging
import os
from typing import Optional

import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash

from app.domain.interfaces import IDatabaseConnection, IUserRepository, IOtpRepository


class MySqlConnection(IDatabaseConnection):
    """Manages a single pymysql connection lifecycle."""

    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        self.host = host or os.environ.get('HOST_BD', 'dev.jonnattan.com')
        self.port = port or int(os.environ.get('PORT_BD', 3306))
        self.user = user or os.environ.get('USER_BD', '----')
        self.password = password or os.environ.get('PASS_BD', '*****')
        self.database = database or os.environ.get('SCHEMA_BD', '*****')
        self._db = None

    def connect(self) -> None:
        try:
            self._db = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor,
            )
        except Exception as exc:
            logging.error("MySqlConnection connect error: %s", exc)
            self._db = None

    def is_connected(self) -> bool:
        return self._db is not None

    def close(self) -> None:
        if self._db is not None:
            self._db.close()
            self._db = None

    @property
    def raw(self):
        if self._db is None:
            self.connect()
        return self._db


class UserRepository(IUserRepository):
    """Handles OAuth user persistence."""

    def __init__(self, db: MySqlConnection):
        self._db = db

    def verify_credentials(self, username: str, password: str) -> Optional[str]:
        user_bd = None
        password_bd = None
        try:
            if not self._db.is_connected():
                self._db.connect()
            cursor = self._db.raw.cursor()
            cursor.execute("select * from oauth where username = %s", (username,))
            results = cursor.fetchall()
            for row in results:
                password_bd = str(row['password'])
                user_bd = str(row['username'])
            if user_bd and password_bd:
                if not check_password_hash(password_bd, password):
                    user_bd = None
            cursor.close()
        except Exception as exc:
            logging.error("UserRepository verify_credentials error: %s", exc)
        return user_bd

    def create_user(self, username: str, password_hash: str) -> None:
        try:
            if not self._db.is_connected():
                self._db.connect()
            cursor = self._db.raw.cursor()
            from datetime import datetime

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO oauth (create_at, username, password) VALUES (%s, %s, %s)",
                (now, username, password_hash),
            )
            self._db.raw.commit()
            cursor.close()
        except Exception as exc:
            logging.error("UserRepository create_user error: %s", exc)
            self._db.raw.rollback()


class OtpRepository(IOtpRepository):
    """Handles OTP persistence."""

    def __init__(self, db: MySqlConnection):
        self._db = db

    def create(self, otp_data) -> None:
        try:
            if not self._db.is_connected():
                self._db.connect()
            cursor = self._db.raw.cursor()
            cursor.execute(
                """
                INSERT INTO Otp (create_at, expirate_at, otp, ref, mail, mobile, status, channel)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    otp_data['create_at'],
                    otp_data['expirate_at'],
                    otp_data['otp'],
                    otp_data['ref'],
                    otp_data['mail'],
                    otp_data['mobile'],
                    otp_data['status'],
                    otp_data['channel'],
                ),
            )
            self._db.raw.commit()
            cursor.close()
        except Exception as exc:
            logging.error("OtpRepository create error: %s", exc)
            self._db.raw.rollback()

    def find_pending_by_channel(self, channel: str):
        try:
            if not self._db.is_connected():
                self._db.connect()
            cursor = self._db.raw.cursor()
            is_mail = '@' in channel and '.' in channel
            sql = (
                "select * from Otp where mail = %s and status = %s"
                if is_mail
                else "select * from Otp where mobile = %s and status = %s"
            )
            cursor.execute(sql, (channel, 'PENDING'))
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as exc:
            logging.error("OtpRepository find_pending_by_channel error: %s", exc)
            return []

    def find_by_reference(self, reference: str):
        try:
            if not self._db.is_connected():
                self._db.connect()
            cursor = self._db.raw.cursor()
            cursor.execute("select * from Otp where ref = %s", (reference,))
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as exc:
            logging.error("OtpRepository find_by_reference error: %s", exc)
            return []

    def burn(self, reference: str, status: str, attempt: int) -> None:
        try:
            if not self._db.is_connected():
                self._db.connect()
            cursor = self._db.raw.cursor()
            from datetime import datetime

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "UPDATE Otp SET status = %s, validate_at = %s, attempt = %s WHERE ref = %s",
                (status, now, attempt, reference),
            )
            self._db.raw.commit()
            cursor.close()
        except Exception as exc:
            logging.error("OtpRepository burn error: %s", exc)
            self._db.raw.rollback()
