import unittest
from unittest.mock import patch

from mail_box.driver import download_mails_and_store


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


#
# class ApplyRulesUnitTest(unittest.TestCase):
#     def test_file_not_exists(self):
#         pass
#
#     def test_invalid_file(self):
#         pass
#
#     def test_str_rule(self):
#         pass
#
#     def test_int_rule(self):
#         pass
#
#     def test_any_predicate(self):
#         pass
#
#     def test_all_predicate(self):
#         pass
