from pydantic import BaseModel, Field


class Cli(BaseModel):
    input: str = Field(default="data/input.csv")
    output: str = Field(default="data/output.csv")
    sum: float
