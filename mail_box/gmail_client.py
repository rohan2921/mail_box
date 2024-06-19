from contextlib import suppress
from functools import partial
from typing import Dict, List, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from mail_box.types import MessageAction


class GmailAPIHandler:
    SCOPES = ["https://mail.google.com/"]

    def __init__(self, credentials_file_path):
        self.credentials_file = credentials_file_path
        self.email_service = build("gmail", "v1", credentials=self.get_creds())

    def get_creds(self) -> Credentials:
        """
        Retrieves the OAuth 2.0 credentials for the user, either from an existing token file or by generating a new one.

        This function attempts to read the user's OAuth 2.0 credentials from a file named "existing_token.json".
        If the file does not exist, or if the credentials are invalid or expired, it will initiate the OAuth 2.0
        authorization flow to obtain new credentials. If new credentials are obtained, they are saved to "existing_token.json"
        for future use.

        Returns:
            google.oauth2.credentials.Credentials: The OAuth 2.0 credentials for the user.

        Notes:
            - Ensure that `self.credentials_file` contains the path to your client secrets file.
            - `self.SCOPES` should be a list of OAuth 2.0 scopes required by your application.

        """
        """

        :return: google.oauth2.credentials.Credentials: The OAuth 2.0 credentials for the user.
        """
        creds = None
        with suppress(FileNotFoundError):
            creds = Credentials.from_authorized_user_file(
                "existing_token.json", scopes=self.SCOPES
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, scopes=self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except ValueError:
                    print("Invalid file format")
            # Saving the credentials for the next run
            with open("existing_token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    def get_mails(self, next_page_token: str = None) -> Tuple[List, str]:
        query_params = {"UserId": "me"}
        if next_page_token:
            query_params["pageToken"] = next_page_token
        resp = self.email_service.users().messages().list(userId="me").execute()
        return resp["messages"], resp["nextPageToken"]

    def get_mail_content(self, mail_infos: List[Dict]) -> List[Dict]:
        """
        Retrieve the full content of specified email messages using batch processing.

        Args:
            mail_infos (List[Dict]): A list of dictionaries containing message metadata with message IDs and other email data.

        Returns:
            List[Dict]: A list of dictionaries containing the full content of the specified messages.
        """
        batch = self.email_service.new_batch_http_request()

        message_data = []
        callback_batch = partial(
            batch.add,
            callback=lambda request, response, err: print(err)
            if err
            else message_data.append(response),
        )
        # calling list here else the values are not evaluated
        list(
            map(
                lambda message: callback_batch(
                    self.email_service.users()
                    .messages()
                    .get(userId="me", id=message["id"])
                ),
                mail_infos,
            )
        )
        batch.execute()
        return message_data

    def modify_mail(self, mail_actions: List[MessageAction]):
        """
        Function to modify mails based on actions
        :param mail_actions: List[MessageAction] containing the mail ids, addLabelIds and removeLabelIds
        :return: None
        """
        list(
            map(
                lambda mail: self.email_service.users()
                .messages()
                .batchModify(
                    userId="me",
                    body={
                        "ids": mail.ids,
                        "addLabelIds": mail.add_labels,
                        "removeLabelIds": mail.remove_labels,
                    },
                )
                .execute(),
                mail_actions,
            )
        )
