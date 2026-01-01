from uuid import uuid4


class TestDBHelper:
    """Вспомогательный класс для работы с тестовыми базами данных."""

    @staticmethod
    def create_test_db_name(postfix: str = "") -> str:
        """Создать уникальное имя для тестовой БД."""
        return f"{str(uuid4())[:6]}_{postfix}"
