from src.models.entities.exam import ExamTable
from src.models.settings.connection import db_connection_handler

class ExamRepository:
    def __init__(self, db_connection):
        self.__db_connection = db_connection

    def insert_exam(
        self,
        protocol_number: int,
        exam_type: str,
        audit: str,
        name: str,
        status: str = "Pendente"
    ) -> None:
        with self.__db_connection as database:
            try:
                user = ExamTable(
                    protocol_number = protocol_number,
                    exam_type = exam_type,
                    audit = audit,
                    name = name,
                    status = status
                )
                database.session.add(user)
                database.session.commit()
            except Exception as exception:
                database.session.rollback()
                raise exception
    
    def list_exams(self):
        with self.__db_connection as database:
            try:
                exams = database.session.query(ExamTable).all()
                return exams
            except Exception as exception:
                raise exception
            
exam_repository = ExamRepository(db_connection_handler)