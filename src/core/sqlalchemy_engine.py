from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy_mixins import ActiveRecordMixin, ReprMixin

# ✅ Replace with your actual DB credentials
DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/parkspacehub'

engine = create_engine(DATABASE_URL)
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


Base.metadata.create_all(engine)



# Used SQLAlchemy Mixin
# we also use ReprMixin which is optional
class BaseModel(Base, ActiveRecordMixin, ReprMixin):
    __abstract__ = True
    __repr__ = ReprMixin.__repr__
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    pass


BaseModel.set_session(session)