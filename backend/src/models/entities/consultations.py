
from sqlalchemy import Column, Integer, String
from src.models.settings.base import Base

class ConsultationTable(Base):
    __tablename__ = 'consultations'
    
    consultation_id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String)
    period = Column(String)
    speciality = Column(String)


    def __repr__(self):
        return f"<Consultation(id={self.consultation_id}, status={self.status}, protocol={self.protocol_code})>"
