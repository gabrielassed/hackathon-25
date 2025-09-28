from sqlalchemy import Column, String, Integer

from src.models.settings.base import Base

class ExamTable(Base):
    __tablename__ = 'exam'

    protocol_number = Column(Integer, primary_key=True)
    exam_type = Column(String)
    audit = Column(String)
    name = Column(String)
    status = Column(String)


    def __repr__(self):
        return f"<ExamTable(protocol_number={self.protocol_number}, name='{self.name}', audit='{self.audit}')>"