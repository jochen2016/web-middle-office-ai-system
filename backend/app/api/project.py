from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.database import get_db
from app.models import Project, ContractPayment, StaffCommission
from app.schemas import (
    ProjectCreate, ProjectUpdate, ProjectStaffConfigSave,
    ProjectProfitResponse, ResponseModel, ListResponse
)

router = APIRouter(prefix="/project", tags=["项目管理"])


@router.get("/get", response_model=ListResponse)
def get_project_list(
    project_name: Optional[str] = None,
    customer_project_name: Optional[str] = None,
    customer_project_code: Optional[str] = None,
    project_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """多条件查询项目"""
    query = db.query(Project)
    
    if project_name:
        query = query.filter(Project.project_name.like(f"%{project_name}%"))
    if customer_project_name:
        query = query.filter(Project.customer_project_name.like(f"%{customer_project_name}%"))
    if customer_project_code:
        query = query.filter(Project.customer_project_code.like(f"%{customer_project_code}%"))
    if project_type:
        query = query.filter(Project.project_type == project_type)
    if status:
        query = query.filter(Project.status == status)
    
    total = query.count()
    offset = (page - 1) * page_size
    projects = query.order_by(Project.id.desc()).offset(offset).limit(page_size).all()
    
    project_list = []
    for p in projects:
        project_list.append({
            "id": p.id,
            "project_name": p.project_name,
            "customer_project_name": p.customer_project_name,
            "customer_project_code": p.customer_project_code,
            "company_name": p.company_name,
            "project_type": p.project_type.value if p.project_type else None,
            "fixed_package_amount": float(p.fixed_package_amount) if p.fixed_package_amount else None,
            "customer_surplus_man_day": p.customer_surplus_man_day,
            "surplus_man_day_status": p.surplus_man_day_status.value if p.surplus_man_day_status else None,
            "status": p.status.value if p.status else None,
            "create_time": p.create_time.isoformat() if p.create_time else None,
        })
    
    return ListResponse(
        data={"list": project_list},
        total=total
    )


@router.post("/create", response_model=ResponseModel)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db)
):
    """新增项目"""
    project = Project(
        project_name=data.project_name,
        customer_project_name=data.customer_project_name,
        customer_project_code=data.customer_project_code,
        company_name=data.company_name,
        address=data.address,
        lng=data.lng,
        lat=data.lat,
        contract_amount=data.contract_amount,
        payment_term=data.payment_term,
        project_type=data.project_type,
        fixed_package_amount=data.fixed_package_amount,
        status=data.status
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return ResponseModel(data={"id": project.id})


@router.put("/update", response_model=ResponseModel)
def update_project(
    data: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """修改项目"""
    project = db.query(Project).filter(Project.id == data.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "project_type" and value:
            value = Project.ProjectType(value)
        elif key == "status" and value:
            value = Project.ProjectStatus(value)
        elif key == "surplus_man_day_status" and value:
            value = Project.SurplusStatus(value)
        setattr(project, key, value)
    
    db.commit()
    
    return ResponseModel(msg="更新成功")


@router.post("/staff/config/save", response_model=ResponseModel)
def save_project_staff_config(
    data: ProjectStaffConfigSave,
    db: Session = Depends(get_db)
):
    """保存项目人员自定义提成单价"""
    from app.models import ProjectStaffConfig
    
    existing = db.query(ProjectStaffConfig).filter(
        ProjectStaffConfig.project_id == data.project_id,
        ProjectStaffConfig.staff_id == data.staff_id
    ).first()
    
    if existing:
        if data.custom_day_commission is not None:
            existing.custom_day_commission = data.custom_day_commission
        db.commit()
        return ResponseModel(msg="更新成功")
    
    config = ProjectStaffConfig(
        project_id=data.project_id,
        staff_id=data.staff_id,
        custom_day_commission=data.custom_day_commission
    )
    db.add(config)
    db.commit()
    
    return ResponseModel(msg="保存成功")


@router.get("/staff/config/list", response_model=ListResponse)
def get_project_staff_config_list(
    project_id: int,
    db: Session = Depends(get_db)
):
    """查询项目人员提成配置"""
    from app.models import ProjectStaffConfig, Staff
    
    configs = db.query(ProjectStaffConfig, Staff).join(
        Staff, ProjectStaffConfig.staff_id == Staff.id
    ).filter(
        ProjectStaffConfig.project_id == project_id
    ).all()
    
    config_list = []
    for config, staff in configs:
        config_list.append({
            "id": config.id,
            "project_id": config.project_id,
            "staff_id": config.staff_id,
            "staff_name": staff.name,
            "staff_level": staff.staff_level.value if staff.staff_level else None,
            "custom_day_commission": config.custom_day_commission,
            "default_day_commission": staff.default_day_commission,
        })
    
    return ListResponse(data={"list": config_list})


@router.delete("/staff/config/del", response_model=ResponseModel)
def delete_project_staff_config(
    id: int,
    db: Session = Depends(get_db)
):
    """删除自定义配置，恢复职级默认价"""
    from app.models import ProjectStaffConfig
    
    config = db.query(ProjectStaffConfig).filter(ProjectStaffConfig.id == id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    db.delete(config)
    db.commit()
    
    return ResponseModel(msg="删除成功")


@router.get("/profit/get", response_model=ResponseModel)
def get_project_profit(
    project_id: int,
    db: Session = Depends(get_db)
):
    """获取项目完整利润、成本、风控、溢量台账数据"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 查询项目最新合同回款记录
    contract = db.query(ContractPayment).filter(
        ContractPayment.project_id == project_id
    ).order_by(ContractPayment.id.desc()).first()
    
    # 计算真实营收
    if project.project_type == Project.ProjectType.DAY_PROJECT:
        # 人天项目：基于回款的人天结算营收
        real_revenue = float(contract.project_cost_man_day) if contract else 0
    else:
        # 整包项目：固定包干总价
        real_revenue = float(project.fixed_package_amount) if project.fixed_package_amount else 0
    
    # 真实毛利 = 真实营收 - 人力成本 - 差旅成本（仅普通报销）
    real_gross_profit = real_revenue - float(contract.project_cost_man_day or 0) - float(contract.project_cost_travel or 0)
    
    profit_data = {
        "project_id": project.id,
        "project_type": project.project_type.value if project.project_type else None,
        "project_name": project.project_name,
        "real_revenue": real_revenue,
        "real_cost_man_day": float(contract.project_cost_man_day) if contract else 0,
        "real_cost_travel": float(contract.project_cost_travel) if contract else 0,
        "real_gross_profit": real_gross_profit,
        "surplus_man_day": project.customer_surplus_man_day or 0,
        "surplus_income": float(contract.project_surplus_income) if contract else 0,
        "surplus_status": project.surplus_man_day_status.value if project.surplus_man_day_status else None,
    }
    
    # 整包特有字段
    if project.project_type == Project.ProjectType.PACKAGE_PROJECT:
        profit_data["fixed_package_amount"] = float(project.fixed_package_amount) if project.fixed_package_amount else None
        profit_data["package_cost_budget"] = float(contract.package_cost_budget) if contract and contract.package_cost_budget else None
        profit_data["package_cost_surplus"] = float(contract.package_cost_surplus) if contract and contract.package_cost_surplus else None
        profit_data["package_risk_status"] = contract.package_risk_status.value if contract and contract.package_risk_status else None
    
    return ResponseModel(data=profit_data)