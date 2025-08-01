from datetime import datetime
from passlib.hash import pbkdf2_sha256
import random
import string
import binascii
from sqlalchemy import Boolean, Column, DateTime, Integer, String, and_
from core.sqlalchemy_engine import Base
from core.sqlalchemy_engine import session, BaseModel



# class Gender(enum.Enum):
#     MALE = 1
#     FEMALE = 2
#     OTHER = 3

class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50))
    middle_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True)
    mobile_number = Column(String(16))
    gender = Column(String(100))  # ❌ No need for `unique=True` here
    enrollment_number = Column(String(255), nullable=True)
    password = Column(String(100))

    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer)

    is_active = Column(Boolean, nullable=False, default=True)


    @classmethod
    def add(cls, data):
        user = User()

        # Always pop the role if it's there
        data.pop('role', None)

        raw_password = data.get('password')
        if not raw_password:
            raw_password = cls._generate_random_password(6)

        data['password'] = cls._hash_password(raw_password)

        user.fill(**data)
        user.save()

        return user, raw_password
    
    @staticmethod
    def _generate_random_password(string_length = 12):
        """Generate a random string of letters, digits and special characters """
        password_characters = string.ascii_letters
        return ''.join(random.choice(password_characters) for i in range(string_length))
    
    @staticmethod
    def get_by_email(email):
        return session.query(User).filter_by(email = email).first()
    
    @staticmethod
    def get_by_id(_id):
        return session.query(User).filter_by(id = _id).first()
    
    @classmethod
    def _hash_password(cls, password_plain):
        hashed_password = pbkdf2_sha256.encrypt(password_plain, rounds = 200000, salt_size = 16)
        return hashed_password
    
    @classmethod
    def _match_password(cls, password_plain, hashed_password):
        return pbkdf2_sha256.verify(password_plain, hashed_password)

    @classmethod
    def update_dict(cls, user_id,  data):
        try:
            query = session.query(User).filter(and_(User.id == user_id)).update(
                data, synchronize_session='evaluate'
            )
            return query
        except Exception as e:
            User.logger.info('Exception while Updating Application.')
            User.logger.info(e)
            return None

    @classmethod
    def authenticate(cls, email, password):
        user = cls.get_by_email(email)
        if user:
            if cls._match_password(password, user.password):
                return user
        return None
