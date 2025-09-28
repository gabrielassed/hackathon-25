from src.models.entities.doctor import DoctorTable
from src.models.settings.connection import db_connection_handler

class DoctorRepository:
    def __init__(self, db_connection):
        self.__db_connection = db_connection

    def create_doctor(self, name: str, specialty: str, city: str = None):
        with self.__db_connection as database:
            try:
                doctor = DoctorTable(
                    name = name,
                    specialty = specialty,
                    city = city
                )
                database.session.add(doctor)
                database.session.commit()
            except Exception as exception:
                database.session.rollback()
                raise exception
    
    def get_doctor_by_id(self, doctor_id: int):
        with self.__db_connection as database:
            try:
                doctor = database.session.query(DoctorTable).filter(DoctorTable.doctor_id == doctor_id).first()
                return doctor
            except Exception as exception:
                raise exception
            
doctor_repository = DoctorRepository(db_connection_handler)