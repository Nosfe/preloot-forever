from pydantic import BaseModel


class Settings(BaseModel):
    target_phase: str
