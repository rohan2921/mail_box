import json
import os
import unittest
from unittest.mock import patch

from mail_box.driver import apply_rules, download_mails_and_store


class DownloadMailsAndStoreUnitTest(unittest.TestCase):
    def setUp(self):
        self.valid_file_path = "/home/rohan/Downloads/client_secret_813044147814-kjiu5odm4r9a31rc8k3vjk6b2q2kaudn.apps.googleusercontent.com.json"
        self.invalid_file_path = "/home/rohan/invalid_creds.json"
        self.nonexistent_file_path = "/home/rohan/nonexistent_creds.json"
        self.get_mails_return = (
            [
                {"id": "19031e86af18bcfb", "threadId": "19031e86af18bcfb"},
                {"id": "19031d40a1999995", "threadId": "19031d40a1999995"},
                {"id": "19031a9e4dfb26f0", "threadId": "1902fc92b02f7ecb"},
            ],
            "jsdahgjkbgfk",
        )

        self.valid_mails_content = [
            {
                "payload": {
                    "headers": [
                        {"name": "From", "value": "user@test.com"},
                        {"name": "To", "value": "appinirohan@gmail.com"},
                        {"name": "Subject", "value": "Unit Test"},
                        {
                            "name": "Date",
                            "value": "'Wed, 19 Jun 2024 12:57:25 +0530 (IST)'",
                        },
                    ]
                },
                "id": "1902f64b74619bbd",
                "snippet": "Thanks Rohan Kumar!",
            }
        ]
        # mail with missing important headers
        self.invalid_mail_content = [
            {
                "payload": {
                    "headers": [
                        {"name": "Subject", "value": "Unit Test"},
                        {
                            "name": "Date",
                            "value": "'Wed, 19 Jun 2024 12:57:25 +0530 (IST)'",
                        },
                    ]
                },
                "id": "1902f64b74619bbd",
                "snippet": "Thanks Rohan Kumar!",
            }
        ]

    @patch("mail_box.gmail_client.GmailAPIHandler")
    @patch("mail_box.db_tables.create_mail_messages")
    def test_download_mails_and_store(
        self, mock_create_mail_messages, mock_GmailAPIHandler
    ):
        # Mocking the GmailAPIHandler instance and its methods
        mock_gmail_api_handler_instance = unittest.mock.MagicMock()
        mock_GmailAPIHandler.return_value = mock_gmail_api_handler_instance
        mock_gmail_api_handler_instance.get_mails.return_value = self.get_mails_return
        mock_gmail_api_handler_instance.get_mail_content.return_value = (
            self.valid_mails_content
        )

        # calling
        download_mails_and_store(self.valid_file_path)

        # Assert
        mock_GmailAPIHandler.assert_called_once_with(self.valid_file_path)
        mock_gmail_api_handler_instance.get_mails.assert_called_once()
        mock_gmail_api_handler_instance.get_mail_content.assert_called_once_with(
            self.get_mails_return[0]
        )
        mock_create_mail_messages.assert_called_once_with(self.valid_mails_content)

    @patch("mail_box.gmail_client.GmailAPIHandler")
    @patch("mail_box.db_tables.create_mail_messages")
    def test_download_mails_file_not_found(
        self, mock_create_mail_messages, MockGmailAPIHandler
    ):
        MockGmailAPIHandler.side_effect = FileNotFoundError

        with self.assertRaises(FileNotFoundError):
            download_mails_and_store(self.valid_file_path)

        # Assert
        MockGmailAPIHandler.assert_called_once_with(self.valid_file_path)
        mock_create_mail_messages.assert_not_called()  # Since failed during handler initialization


class ApplyRulesUnitTest(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_files"
        os.makedirs(self.test_dir, exist_ok=True)
        self.valid_content = {
            "predicate": "any",
            "rules": [
                {"field_name": "subject", "predicate": "contains", "value": "Test"},
                {"field_name": "days", "predicate": "greater than", "value": 5},
            ],
        }

    def tearDown(self):
        for filename in os.listdir(self.test_dir):
            file_path = os.path.join(self.test_dir, filename)
            os.unlink(file_path)
        os.rmdir(self.test_dir)

    def create_test_file(self, filename, content):
        file_path = os.path.join(self.test_dir, filename)
        with open(file_path, "w") as f:
            f.write(json.dumps(content))
        return file_path

    @patch("mail_box.db_tables.filter_mail_messages")
    def test_file_not_exists(self, mock_filter_mail_messages):
        with self.assertRaises(FileNotFoundError):
            apply_rules("non_existent_file.json")
        mock_filter_mail_messages.assert_not_called()

    @patch("mail_box.db_tables.filter_mail_messages")
    @patch("mail_box.rules.RuleBase.get_rule")
    def test_any_predicate(self, mock_get_rule, mock_filter_mail_messages):
        mock_filter_mail_messages.return_value = []
        mock_rule = unittest.mock.MagicMock()
        mock_rule.filter.side_effect = ["filter_1", "filter_2"]
        mock_get_rule.return_value = mock_rule

        file_path = self.create_test_file("any_rule.json", self.valid_content)
        with patch("mail_box.driver.operator.or_") as mock_operator_or:
            mock_operator_or.return_value = "combined_filter"
            apply_rules(file_path)
            mock_operator_or.assert_called()
        mock_filter_mail_messages.assert_called_with("combined_filter")

    @patch("mail_box.db_tables.filter_mail_messages")
    @patch("mail_box.rules.RuleBase.get_rule")
    def test_all_predicate(self, mock_get_rule, mock_filter_mail_messages):
        mock_filter_mail_messages.return_value = []
        mock_rule = unittest.mock.MagicMock()
        mock_rule.filter.side_effect = ["filter_1", "filter_2"]
        mock_get_rule.return_value = mock_rule

        file_path = self.create_test_file("all_rule.json", self.valid_content)
        with patch("mail_box.driver.operator.and_") as mock_operator_and:
            mock_operator_and.return_value = "combined_filter"
            apply_rules(file_path)
            mock_operator_and.assert_called()
        mock_filter_mail_messages.assert_called_with("combined_filter")
