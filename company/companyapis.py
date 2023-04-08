from fastapi import APIRouter

router = APIRouter()

@router.get('/')
def get_company_name():
    return {"companyname":"infosys"}

@router.get('/employees')
def get_employee_numbers():
    return 137