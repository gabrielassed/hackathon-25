from sqlalchemy import Column, String, DateTime, func, Text

from src.models.settings.base import Base

class UserTable():

    __tablename__ = 'users'

    user_id = Column(String, primary_key=True, unique=True)  # UUID
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(120), nullable=False)
    phone = Column(String(20))
    cpf = Column(String(14), unique=True)
    email = Column(String(160), nullable=False, unique=True)
    username = Column(String(80), nullable=False, unique=True)
    password_hash = Column(Text)  # nunca em claro
    role = Column(String(20), nullable=False)  # patient | doctor | approver | admin

    # se médico, campo específico
    crm_number = Column(String(30))   # se role=doctor
    crm_state = Column(String(2))
    department = Column(String(120)) # se role=approver

    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email}, role={self.role})>"
