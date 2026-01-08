from pydantic import BaseModel


class LabeledValue(BaseModel):
    value: str
    label: str
