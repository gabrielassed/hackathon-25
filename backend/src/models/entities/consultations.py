from datetime import date
from src.models.entities import doctor
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from src.models.settings.base import Base

class ConsultationTable(Base):
    __tablename__ = 'consultation'

    consultation_id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey(doctor.DoctorTable.doctor_id), primary_key=True)
    consultation_date = Column(DateTime, nullable=False)


    def __repr__(self):
        return f"<Consultation(id={self.consultation_id}, status={self.status}, protocol={self.protocol_code})>"
