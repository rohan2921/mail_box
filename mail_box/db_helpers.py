from alembic import command
from alembic.config import Config
from sqlmodel import create_engine

# DATABASE_USER = os.environ["DATABASE_USER"]
# DATABASE_PASSWORD = os.environ["DATABASE_PASSWORD"]
# DATABASE_HOST = os.environ["DATABASE_HOST"]
# DATABASE_PORT = os.environ["DATABASE_PORT"]
# DATABASE_NAME = os.environ["DATABASE_NAME"]
# DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
DATABASE_URL = "postgresql://scp:scp@172.18.0.2:5432/mail_box"
engine = create_engine(DATABASE_URL)


def run_migrations():
    """
    Make sure environment variables are for database url before running migrations
    :return:
    """
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
