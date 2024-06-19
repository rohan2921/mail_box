from datetime import datetime
from email.utils import parsedate_to_datetime

from sqlmodel import Field, Session, SQLModel, select

from .db_helpers import engine


class MailMessage(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    mail_id: str
    from_email: str
    to_email: str
    subject: str
    message: str
    timestamp: datetime
    __tablename__ = "mail_message"


def create_mail_messages(mail_infos):
    objs = [
        MailMessage(
            mail_id=mail["id"],
            from_email=mail_headers["From"],
            to_email=mail_headers["To"],
            timestamp=parsedate_to_datetime(mail_headers["Date"]),
            message=mail["snippet"],
            subject=mail_headers.get("Subject", ""),
        )
        for mail in mail_infos
        for mail_headers in [
            {header["name"]: header["value"] for header in mail["payload"]["headers"]}
        ]
    ]
    with Session(engine) as session:
        session.add_all(objs)
        session.commit()


def filter_mail_messages(filters):
    query = select(MailMessage).where(filters)
    with Session(engine) as session:
        return session.exec(query).all()
