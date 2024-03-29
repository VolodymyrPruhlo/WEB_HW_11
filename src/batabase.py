from sqlalchemy.engine import create_engine
import contacts.models
from sqlalchemy.orm import sessionmaker


DBsession = None


def connect():
    global DBsession
    engine = create_engine("postgresql://postgres:1111@localhost:5432/web_hw_11")

    for base in [contacts.models.Base]:
        base.metadata.bind = engine
        base.metadata.create_all(engine)

    DBsession = sessionmaker(bind=engine)


def get_database():
    if DBsession is None:
        connect()

    db = DBsession()

    try:
        yield db
    finally:
        db.close()
