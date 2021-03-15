from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer, DATETIME
import datetime
import config

engine = create_engine(config.DATABASE_NAME)
Session = sessionmaker(bind=engine)

Base = declarative_base()


class Request(Base):
    __tablename__ = 'request'
    id = Column(Integer, primary_key=True)
    host = Column(String)
    method = Column(String)
    code = Column(String)
    headers = Column(String)
    release_date = Column(DATETIME)

    def __init__(self, method, code, headers, host: str):
        self.host = host
        self.method = method
        self.code = code
        self.headers = headers
        self.release_date = datetime.datetime.now()


Base.metadata.create_all(engine)
