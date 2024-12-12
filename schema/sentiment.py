from pydantic import BaseModel

class SummaryResponseSchema(BaseModel):
    summary: str