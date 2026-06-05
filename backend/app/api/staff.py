from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Staff
from app.schemas import StaffCreate, StaffUpdate, ResponseModel, ListResponse

router = APIRouter(prefix="/staff", tags=["员工管理"])

# 职级默认定价
LEVEL_PRICE_MAP = {
    "p0": {"day_price": 600, "day_commission": 50},
    "p1-1": {"day_price": 800, "day_commission": 120},
    "p1-2": {"day_price": 1000, "day_commission": 220},
    "p1-3": {"day_price": 1200, "day_commission": 300},
}


@router.get("/list", response_model=ListResponse)
def get_staff_list(
    name: str = None,
    department: str = None,
    staff_level: str = None,
    status: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """员工列表查询"""
    query = db.query(Staff)
    
    if name:
        query = query.filter(Staff.name.like(f"%{name}%"))
    if department:
        query = query.filter(Staff.department == department)
    if staff_level:
        query = query.filter(Staff.staff_level == staff_level)
    if status:
        query = query.filter(Staff.status == status)
    
    total = query.count()
    offset = (page - 1) * page_size
    staffs = query.order_by(Staff.id.desc()).offset(offset).limit(page_size).all()
    
    staff_list = []
    for s in staffs:
        staff_list.append({
            "id": s.id,
            "feishu_uid": s.feishu_uid,
            "name": s.name,
            "department": s.department,
            "staff_level": s.staff_level.value if s.staff_level else None,
            "base_salary": float(s.base_salary) if s.base_salary else 0,
            "default_day_price": s.default_day_price,
            "default_day_commission": s.default_day_commission,
            "day_commission_rate": float(s.day_commission_rate) if s.day_commission_rate else 0,
            "package_commission_rate": float(s.package_commission_rate) if s.package_commission_rate else 0,
            "status": s.status.value if s.status else None,
            "create_time": s.create_time.isoformat() if s.create_time else None,
        })
    
    return ListResponse(data={"list": staff_list}, total=total)


@router.post("/create", response_model=ResponseModel)
def create_staff(
    data: StaffCreate,
    db: Session = Depends(get_db)
):
    """新增员工"""
    staff = Staff(
        feishu_uid=data.feishu_uid,
        name=data.name,
        department=data.department,
        staff_level=data.staff_level,
        base_salary=data.base_salary,
        default_day_price=data.default_day_price,
        default_day_commission=data.default_day_commission,
        day_commission_rate=data.day_commission_rate,
        package_commission_rate=data.package_commission_rate,
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    
    return ResponseModel(data={"id": staff.id})


@router.put("/update", response_model=ResponseModel)
def update_staff(
    data: StaffUpdate,
    db: Session = Depends(get_db)
):
    """更新员工"""
    staff = db.query(Staff).filter(Staff.id == data.id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "staff_level" and value:
            value = Staff.StaffLevel(value)
        elif key == "status" and value:
            value = Staff.StaffStatus(value)
        setattr(staff, key, value)
    
    db.commit()
    
    return ResponseModel(msg="更新成功")


@router.delete("/delete", response_model=ResponseModel)
def delete_staff(
    id: int,
    db: Session = Depends(get_db)
):
    """删除员工"""
    staff = db.query(Staff).filter(Staff.id == id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    db.delete(staff)
    db.commit()
    
    return ResponseModel(msg="删除成功")