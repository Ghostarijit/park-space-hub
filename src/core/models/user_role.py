from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.sqlalchemy_engine import Base
from core.sqlalchemy_engine import session, BaseModel

class UserRole(BaseModel):
    __tablename__ = 'user_roles'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String)  # e.g., 'admin', 'owner', 'seeker'

    def __repr__(self):
        return f"<UserRole(name='{self.name}')>"
    
    @classmethod
    def add(cls, data):
        user_role = UserRole()
        user_role.fill(**data)
        user_role.save()
        return user_role
    
    @classmethod
    def get_by_name(cls, name):
        role = session.query(cls).filter_by(name=name).first()
        session.close()
        return role
    @classmethod
    def get_by_user_id(cls, user_id):
        role = session.query(cls).filter_by(user_id=user_id).first()
        session.close()
        return role