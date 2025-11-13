from pydantic import BaseModel

class SubnetRequest(BaseModel):
    cidr: str