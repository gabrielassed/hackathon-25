from src.models.entities.users import UserTable
from src.models.repository.user_repository import UserRepository
from src.errors.error_types.http_bad_request import HttpBadRequestError

import re

class UserCreatorController:
    """
    Controller responsável por validar os dados de criação de usuário e delegar ao repositório.
    """

    _ROLE_CHOICES = {"patient", "doctor", "approver", "admin"}
    _STATUS_CHOICES = {"active", "inactive", "blocked"}

    _re_only_letters = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ'´`^~\s-]+$")  # aceita acentos, espaços e hífen
    _re_email = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    _re_username = re.compile(r"^[a-zA-Z0-9_\.]{3,80}$")
    _re_phone = re.compile(r"^[0-9()\-\s+]{8,20}$")
    _re_cpf_digits = re.compile(r"^\d{11}$")
    _re_cpf_mask = re.compile(r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$")
    _re_uf = re.compile(r"^[A-Z]{2}$")

    def __init__(self, user_repository: UserRepository) -> None:
        self.__user_repository = user_repository

    def create(self, user_info: dict) -> dict:
        """
        Espera em user_info (mínimo):
          first_name, last_name, email, username, role, password_hash
        Opcionais:
          phone, cpf, crm_number, crm_state, department, status
        """
        # Extrai campos com defaults
        first_name = user_info.get("first_name", "").strip()
        last_name = user_info.get("last_name", "").strip()
        phone = (user_info.get("phone") or "").strip()
        cpf = (user_info.get("cpf") or "").strip()
        email = (user_info.get("email") or "").strip().lower()
        username = (user_info.get("username") or "").strip()
        password_hash = (user_info.get("password_hash") or "").strip()
        role = (user_info.get("role") or "").strip().lower()

        crm_number = (user_info.get("crm_number") or "").strip()
        crm_state = (user_info.get("crm_state") or "").strip().upper() if user_info.get("crm_state") else ""
        department = (user_info.get("department") or "").strip()
        status = (user_info.get("status") or "active").strip().lower()

        # Validações
        self.__validate_required_fields(first_name, last_name, email, username, role, password_hash)
        self.__validate_names(first_name, last_name)
        self.__validate_email(email)
        self.__validate_username(username)
        self.__validate_phone(phone)
        self.__validate_cpf(cpf)
        self.__validate_status(status)
        self.__validate_role_and_dependents(role, crm_number, crm_state, department)

        # Persiste
        self.__insert_user_in_db(
            first_name=first_name,
            last_name=last_name,
            phone=phone or None,
            cpf=cpf or None,
            email=email,
            username=username,
            password_hash=password_hash or None,
            role=role,
            crm_number=crm_number or None,
            crm_state=crm_state or None,
            department=department or None,
            status=status
        )

        # Resposta padronizada
        return self.__format_response({
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone or None,
            "cpf": cpf or None,
            "email": email,
            "username": username,
            "role": role,
            "crm_number": crm_number or None,
            "crm_state": crm_state or None,
            "department": department or None,
            "status": status
        })

    # --------- Validações ---------

    def __validate_required_fields(self, first_name, last_name, email, username, role, password_hash) -> None:
        missing = []
        if not first_name: missing.append("first_name")
        if not last_name: missing.append("last_name")
        if not email: missing.append("email")
        if not username: missing.append("username")
        if not role: missing.append("role")
        if not password_hash: missing.append("password_hash")
        if missing:
            raise HttpBadRequestError(f"Missing required fields: {', '.join(missing)}")

    def __validate_names(self, first_name: str, last_name: str) -> None:
        if not self._re_only_letters.match(first_name) or not self._re_only_letters.match(last_name):
            raise HttpBadRequestError("First name and last name must contain only letters/spaces/hyphens (accents allowed).")

    def __validate_email(self, email: str) -> None:
        if not self._re_email.match(email):
            raise HttpBadRequestError("Invalid email format.")

    def __validate_username(self, username: str) -> None:
        if not self._re_username.match(username):
            raise HttpBadRequestError("Username must be 3-80 chars and contain only letters, numbers, underscores or dots.")

    def __validate_phone(self, phone: str) -> None:
        if phone and not self._re_phone.match(phone):
            raise HttpBadRequestError("Invalid phone format.")

    def __validate_cpf(self, cpf: str) -> None:
        if not cpf:
            return
        if not (self._re_cpf_digits.match(cpf) or self._re_cpf_mask.match(cpf)):
            raise HttpBadRequestError("CPF must be 11 digits or formatted as 000.000.000-00.")
        # (Opcional) implementar validação de dígitos verificadores do CPF.

    def __validate_status(self, status: str) -> None:
        if status and status not in self._STATUS_CHOICES:
            raise HttpBadRequestError(f"Invalid status. Allowed: {', '.join(sorted(self._STATUS_CHOICES))}")

    def __validate_role_and_dependents(self, role: str, crm_number: str, crm_state: str, department: str) -> None:
        if role not in self._ROLE_CHOICES:
            raise HttpBadRequestError(f"Invalid role. Allowed: {', '.join(sorted(self._ROLE_CHOICES))}")

        if role == "doctor":
            if not crm_number:
                raise HttpBadRequestError("crm_number is required when role=doctor.")
            if not crm_state or not self._re_uf.match(crm_state):
                raise HttpBadRequestError("crm_state must be a valid UF (2 uppercase letters) when role=doctor.")

        if role == "approver" and not department:
            raise HttpBadRequestError("department is required when role=approver.")

    # --------- Persistência ---------

    def __insert_user_in_db(
        self,
        *,
        first_name: str,
        last_name: str,
        phone: str | None,
        cpf: str | None,
        email: str,
        username: str,
        password_hash: str | None,
        role: str,
        crm_number: str | None,
        crm_state: str | None,
        department: str | None,
        status: str
    ) -> None:
        try:
            self.__user_repository.insert_user(
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
        except Exception as exc:
            # Você pode tratar exceções específicas de unique constraint aqui, se quiser.
            # Ex.: IntegrityError do SQLAlchemy para email/username/cpf duplicados.
            raise exc

    # --------- Formatação de resposta ---------

    def __format_response(self, user_attrs: dict) -> dict:
        return {
            "data": {
                "type": "User",
                "count": 1,
                "attributes": user_attrs
            }
        }
