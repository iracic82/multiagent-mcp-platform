from fastapi import APIRouter
from models.subnet_model import SubnetRequest
from services.subnet_calc import calculate_subnet

router = APIRouter(prefix="/subnet", tags=["Subnet Calculator"])

@router.post("/calculate")
def subnet_calculator(req: SubnetRequest):
    return calculate_subnet(req.cidr)