from sqlalchemy.orm.exc import NoResultFound
from src.models.entities.users import UserTable  # ajuste o caminho do seu modelo

class UserRepository:
    def __init__(self, db_connection):
        self.__db_connection = db_connection

    def insert_user(
        self,
        first_name: str,
        last_name: str,
        phone: str,
        cpf: str,
        email: str,
        username: str,
        password_hash: str,
        role: str,
        crm_number: str = None,
        crm_state: str = None,
        department: str = None,
        status: str = "active"
    ) -> None:
        with self.__db_connection as database:
            try:
                user = UserTable(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    cpf=cpf,
                    email=email,
                    username=username,
                    password_hash=password_hash,
                    role=role,
                    crm_number=crm_number,
                    crm_state=crm_state,
                    department=department,
                    status=status
                )
                database.session.add(user)
                database.session.commit()
            except Exception as exception:
                database.session.rollback()
                raise exception

    def get_user_by_id(self, user_id: str):
        with self.__db_connection as database:
            try:
                user = (
                    database.session
                    .query(UserTable)
                    .filter(UserTable.user_id == user_id)
                    .one()
                )
                return user
            except NoResultFound:
                return None

    def get_user_by_email(self, email: str):
        with self.__db_connection as database:
            try:
                user = (
                    database.session
                    .query(UserTable)
                    .filter(UserTable.email == email)
                    .one()
                )
                return user
            except NoResultFound:
                return None

    def update_user_status(self, user_id: str, new_status: str) -> None:
        with self.__db_connection as database:
            try:
                user = (
                    database.session
                    .query(UserTable)
                    .filter(UserTable.user_id == user_id)
                    .one()
                )
                user.status = new_status
                database.session.commit()
            except Exception as exception:
                database.session.rollback()
                raise exception

    def delete_user(self, user_id: str) -> None:
        with self.__db_connection as database:
            try:
                user = (
                    database.session
                    .query(UserTable)
                    .filter(UserTable.user_id == user_id)
                    .one()
                )
                database.session.delete(user)
                database.session.commit()
            except Exception as exception:
                database.session.rollback()
                raise exception

user_repository = UserRepository()