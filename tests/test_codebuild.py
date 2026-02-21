"""Tests for cftcli.codebuild module."""

import unittest
from unittest.mock import patch, MagicMock
from cftcli.codebuild import s3arn_to_s3url, download_artifact


class TestCodebuild(unittest.TestCase):
    """Test codebuild module functions."""

    def test_s3arn_to_s3url(self):
        """Test converting S3 ARN to S3 URL."""
        arn = 'arn:aws:s3:::my-bucket/path/to/object'
        result = s3arn_to_s3url(arn)
        self.assertEqual(result, 's3://my-bucket/path/to/object')

    def test_s3arn_to_s3url_nested(self):
        """Test converting nested S3 ARN to S3 URL."""
        arn = 'arn:aws:s3:::bucket/folder/subfolder/file.zip'
        result = s3arn_to_s3url(arn)
        self.assertEqual(result, 's3://bucket/folder/subfolder/file.zip')

    @patch('cftcli.codebuild.S3CLIENT')
    def test_download_artifact_success(self, mock_s3):
        """Test successful artifact download."""
        mock_s3.download_file.return_value = None
        arn = 'arn:aws:s3:::bucket/file.zip'
        result = download_artifact(arn, 'output.zip')
        self.assertIn('SUCCESS', result)
        mock_s3.download_file.assert_called_once()

    @patch('cftcli.codebuild.S3CLIENT')
    def test_download_artifact_failure(self, mock_s3):
        """Test failed artifact download."""
        mock_s3.download_file.side_effect = Exception('Download failed')
        arn = 'arn:aws:s3:::bucket/file.zip'
        result = download_artifact(arn, 'output.zip')
        self.assertIn('FAILED', result)


if __name__ == '__main__':
    unittest.main()
