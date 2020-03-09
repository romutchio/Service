from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import os

user = os.environ['POSTGRES_USER']
pwd = os.environ['POSTGRES_PASSWORD']
db = os.environ['POSTGRES_DB']
host = 'db'
port = '5432'
engine = create_engine(f'postgres://{user}:{pwd}@{host}:{port}/{db}', isolation_level="REPEATABLE_READ")

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import database.models
    Base.metadata.create_all(bind=engine)


def init_default_values():
    from database.models import Abonent
    test_data = [
        Abonent('26c940a1-7228-4ea2-a3bc-e6460b172040', 'Петров Иван Сергеевич', 1700, 300, True),
        Abonent('7badc8f8-65bc-449a-8cde-855234ac63e1', 'Kazitsky Jason', 200, 200, True),
        Abonent('5597cc3d-c948-48a0-b711-393edf20d9c0', 'Пархоменко Антон Александрович', 10, 300, True),
        Abonent('867f0924-a917-4711-939b-90b179a96392', 'Петечкин Петр Измаилович', 1000000, 1, False)
    ]
    db_session.query(Abonent).delete()
    db_session.add_all(test_data)
    db_session.commit()
