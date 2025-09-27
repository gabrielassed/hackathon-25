from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, func

from src.models.settings.base import Base

class ExamTable(Base):
    __tablename__ = 'exam'

    exam_id = Column(String, primary_key=True, unique=True)  # UUID

    patient_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    requesting_doctor_id = Column(String, ForeignKey("users.user_id"))
    authorized_by = Column(String, ForeignKey("users.user_id"))

    procedure_name = Column(String(300))
    tiss_code = Column(String(40))

    file_url = Column(Text)
    file_mime_type = Column(String(80))
    file_size_bytes = Column(Integer)
    ocr_text = Column(Text)

    auth_status = Column(String(30), nullable=False, default="requested")
    authorized_at = Column(DateTime)
    reason = Column(Text)

    requested_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Exam(id={self.exam_id}, patient={self.patient_id}, status={self.auth_status})>"