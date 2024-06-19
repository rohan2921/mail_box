import json
import logging
import operator
import sys
from functools import reduce

from mail_box import db_tables, gmail_client, rules
from mail_box.types import MessageAction

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
try:
    HANDLER = logger.handlers[0]
    HANDLER.setFormatter(
        logging.Formatter(
            "%(levelname)s | %(asctime)s | %(filename)s | %(lineno)d | %(funcName)s | %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
    )
except Exception:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(levelname)s | %(asctime)s | %(filename)s | %(lineno)d | %(funcName)s | %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)


LABELS_ACTIONS_MAP = {
    "mark as read": {
        "remove_labels": [
            "UNREAD",
        ],
    },
    "move to folder": {
        "add_labels": [
            "Label_5199249029799924795",
        ],
        "remove_labels": ["INBOX"],
    },
}


def download_mails_and_store(file_path: str):
    """
    Fetches mails from gmail and stores it to our database
    :param file_path: path to the creds file
    :return: None
    """
    gmail_api_handler = gmail_client.GmailAPIHandler(file_path)
    # Fetching emails from the account
    mails, next_page_token = gmail_api_handler.get_mails()
    mail_infos = gmail_api_handler.get_mail_content(mails[:10])
    db_tables.create_mail_messages(mail_infos)


def apply_rules(file_path: str) -> list[db_tables.MailMessage]:
    """
     Make sure that the json file is in the following format
     {
         "predicate": "all" / "any",
         "rules": [
                     {
                         "field_name": supported options ("from_email", "to_email", "subject", "days", "message"),
                         "predicate": supported options ("greater than", "less than", "contains", "does not contain",
                          "equals", "not equals"),
                         "value": "Integer or String"
                     }
         ],
    }

     :param file_path: path to the rules file
     :return: list[db_tables.MailMessage]
    """
    with open(file_path, "r") as f:
        rule_data = json.loads(f.read())
    rule_filters = [
        rules.RuleBase.get_rule(type(rule["value"]).__name__)(**rule).filter()
        for rule in rule_data["rules"]
    ]
    opr = operator.and_ if rule_data["predicate"].lower() == "all" else operator.or_
    final_filter = reduce(opr, rule_filters)
    messages = db_tables.filter_mail_messages(final_filter)
    return messages


def perform_actions(
    filepath: str, messages: list[db_tables.MailMessage], actions: list[str]
):
    """
    Please create a label as TEST_FOLDER in your  gmail before using this.
    If 'move to folder' action is given then the filtered mails will be moved to TEST_FOLDER label
    :param filepath: path to the creds file
    :param messages: list of MailMessage objects
    :param actions: there are two options currently ("mark as read", "move to folder")
    :return: None
    """
    message_ids = [message.mail_id for message in messages]
    message_actions = [
        MessageAction(ids=message_ids, **LABELS_ACTIONS_MAP[action])
        for action in actions
    ]
    print(message_actions)
    gmail_api_handler = gmail_client.GmailAPIHandler(filepath)
    gmail_api_handler.modify_mail(message_actions)
