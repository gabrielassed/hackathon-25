from sqlalchemy import Column, String, DateTime, ForeignKey, func, CheckConstraint, Text
from src.models.settings.base import Base

class ConsultationTable(Base):
    __tablename__ = 'consultation'

    consultation_id = Column(String, primary_key=True, unique=True)  # UUID
    title = Column(String(140))
    description = Column(Text)

    scheduled_start = Column(DateTime, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="Agendada")
    protocol_code = Column(String(40), nullable=False, unique=True)
    channel = Column(String(20), nullable=False, default="chatbot")
    location = Column(String(160))
    specialty = Column(String(120))

    patient_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    doctor_id = Column(String, ForeignKey("users.user_id"), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


    def __repr__(self):
        return f"<Consultation(id={self.consultation_id}, status={self.status}, protocol={self.protocol_code})>"
