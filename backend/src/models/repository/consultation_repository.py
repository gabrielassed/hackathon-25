from datetime import datetime
from src.models.entities.consultations import ConsultationTable
from src.models.settings.connection import db_connection_handler

class ConsultationRepository:
    def __init__(self, db_connection):
        self.__db_connection = db_connection

    def insert_consultation(
        self,
        city: str,
        speciality: str,
        period: str
    ) -> None:
        with self.__db_connection as database:
            try:
                consultation = ConsultationTable(
                    city = city,
                    period = period,
                    speciality = speciality
                )
                database.session.add(consultation)
                database.session.commit()
            except Exception as exception:
                database.session.rollback()
                raise exception
            
    def list_consultations(self):
        with self.__db_connection as database:
            try:
                consultations = database.session.query(ConsultationTable).all()
                return consultations
            except Exception as exception:
                raise exception
            
consultation_repository = ConsultationRepository(db_connection_handler)