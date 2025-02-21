import bcrypt


class PasswordService:
    @staticmethod
    def get_password_hash(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            password.encode(),
            hashed_password.encode(),
        )
