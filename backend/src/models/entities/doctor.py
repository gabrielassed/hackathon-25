from sqlalchemy import Column, Integer, String
from src.models.settings.base import Base

class DoctorTable(Base):
    __tablename__ = 'doctor'

    doctor_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    specialty = Column(String(100), nullable=False)
    city = Column(String(100))

    def __repr__(self):
        return f"<Doctor(id={self.doctor_id}, name={self.name}, specialty={self.specialty})>"