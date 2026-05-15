import pytest
from unittest.mock import patch, MagicMock

from app.legacy.utilaws import AwsUtil


class TestAwsUtil:
    @patch.dict("os.environ", {
        "AWS_ACCESS_KEY": "ak", "AWS_SECRET_KEY": "sk",
        "AWS_PINPOINT_APP_ID": "app", "AWS_S3_BUCKET": "bucket"
    })
    @patch("app.legacy.utilaws.boto3.client")
    @patch("app.legacy.utilaws.boto3.Session")
    def test_init(self, mock_session_cls, mock_client):
        mock_session = MagicMock()
        mock_session.get_available_resources.return_value = ["s3"]
        mock_session_cls.return_value = mock_session
        aws = AwsUtil()
        assert aws.sns is not None
        assert aws.pinpoint is not None

    @patch.dict("os.environ", {
        "AWS_ACCESS_KEY": "ak", "AWS_SECRET_KEY": "sk",
        "AWS_PINPOINT_APP_ID": "app", "AWS_S3_BUCKET": "bucket"
    })
    @patch("app.legacy.utilaws.boto3.client")
    @patch("app.legacy.utilaws.boto3.Session")
    def test_test_aws(self, mock_session_cls, mock_client):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        aws = AwsUtil()
        data, code = aws.testAws()
        assert code == 200

    @patch.dict("os.environ", {
        "AWS_ACCESS_KEY": "ak", "AWS_SECRET_KEY": "sk",
        "AWS_PINPOINT_APP_ID": "app", "AWS_S3_BUCKET": "bucket"
    })
    @patch("app.legacy.utilaws.boto3.client")
    @patch("app.legacy.utilaws.boto3.Session")
    def test_request_process_s3_list(self, mock_session_cls, mock_client):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        aws = AwsUtil()
        req = MagicMock()
        data, code = aws.request_process(req, "s3/list")
        assert code == 200

    @patch.dict("os.environ", {
        "AWS_ACCESS_KEY": "ak", "AWS_SECRET_KEY": "sk",
        "AWS_PINPOINT_APP_ID": "app", "AWS_S3_BUCKET": "bucket"
    })
    @patch("app.legacy.utilaws.boto3.client")
    @patch("app.legacy.utilaws.boto3.Session")
    def test_request_process_pinpoint_info(self, mock_session_cls, mock_client):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        aws = AwsUtil()
        req = MagicMock()
        data, code = aws.request_process(req, "pinpoint/info")
        assert code == 200

    @patch.dict("os.environ", {
        "AWS_ACCESS_KEY": "ak", "AWS_SECRET_KEY": "sk",
        "AWS_PINPOINT_APP_ID": "app", "AWS_S3_BUCKET": "bucket"
    })
    @patch("app.legacy.utilaws.boto3.client")
    @patch("app.legacy.utilaws.boto3.Session")
    def test_request_process_unknown(self, mock_session_cls, mock_client):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        aws = AwsUtil()
        req = MagicMock()
        data, code = aws.request_process(req, "unknown")
        assert code == 409
