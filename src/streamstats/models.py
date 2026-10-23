from typing import Literal

from pydantic import AwareDatetime, BaseModel, Field, field_validator


class Event(BaseModel):
    """создаю класс события и проверяю корректность введённых данных"""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    timestamp: AwareDatetime
    source: str = Field(min_length=1)
    message: str

    @field_validator("source")
    @classmethod
    def check_source(cls, source: str) -> str:
        '''проверяю, что источник не пустая строка (не состоит только из пробельных символов)'''
        if source.strip() == "":
            raise ValueError("некорректный формат source")
        return source
