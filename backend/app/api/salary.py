from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Staff, StaffCommission, SalaryBill, ContractPayment, Project
from app.schemas import CommissionAdd, SalaryBillCreate, ResponseModel, ListResponse
from app.services.redis_service import redis_queue
from app.config import get_settings
from decimal import Decimal
import uuid
from datetime import datetime

router = APIRouter(prefix="/salary", tags=["薪资提成"])
settings = get_settings()


@router.get("/staff/config", response_model=ResponseModel)
def get_staff_salary_config(
    staff_id: int,
    db: Session = Depends(get_db)
):
    """获取员工薪资提成配置"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    return ResponseModel(data={
        "staff_id": staff.id,
        "name": staff.name,
        "staff_level": staff.staff_level.value if staff.staff_level else None,
        "base_salary": float(staff.base_salary) if staff.base_salary else 0,
        "default_day_price": staff.default_day_price,
        "default_day_commission": staff.default_day_commission,
        "day_commission_rate": float(staff.day_commission_rate) if staff.day_commission_rate else 0,
        "package_commission_rate": float(staff.package_commission_rate) if staff.package_commission_rate else 0,
    })


@router.post("/staff/commission/add", response_model=ResponseModel)
def add_staff_commission(
    data: CommissionAdd,
    db: Session = Depends(get_db)
):
    """新增项目提成（自动核算、更新项目成本与整包风控）"""
    staff = db.query(Staff).filter(Staff.id == data.staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 计算提成
    total_commission = float(data.day_commission_amount or 0) + float(data.package_bonus_amount or 0)
    
    # 创建提成记录
    commission = StaffCommission(
        staff_id=data.staff_id,
        project_id=data.project_id,
        payment_id=data.payment_id,
        commission_type=data.commission_type,
        day_commission_amount=data.day_commission_amount or 0,
        package_bonus_amount=data.package_bonus_amount or 0,
        total_commission=total_commission,
        project_day_commission=data.project_day_commission,
        settle_status=StaffCommission.SettleStatus.PENDING
    )
    db.add(commission)
    db.commit()
    db.refresh(commission)
    
    # 更新项目人力成本
    contract = db.query(ContractPayment).filter(
        ContractPayment.project_id == data.project_id
    ).order_by(ContractPayment.id.desc()).first()
    
    if contract:
        contract.project_cost_man_day = float(contract.project_cost_man_day or 0) + total_commission
        
        # 重新计算毛利
        contract.project_gross_profit = (
            float(contract.project_surplus_income or 0) if project.project_type == Project.ProjectType.DAY_PROJECT 
            else float(project.fixed_package_amount or 0)
        ) - float(contract.project_cost_man_day) - float(contract.project_cost_travel or 0)
        
        # 整包项目：更新成本剩余和风险状态
        if project.project_type == Project.ProjectType.PACKAGE_PROJECT:
            if contract.package_cost_budget:
                contract.package_cost_surplus = float(contract.package_cost_budget) - float(contract.project_cost_man_day)
                # 判断风险状态
                if contract.package_cost_surplus < 0:
                    contract.package_risk_status = ContractPayment.RiskStatus.LOSS
                elif contract.package_cost_surplus < contract.package_cost_budget * 0.2:
                    contract.package_risk_status = ContractPayment.RiskStatus.WARNING
                else:
                    contract.package_risk_status = ContractPayment.RiskStatus.NORMAL
        
        db.commit()
    
    return ResponseModel(data={"id": commission.id}, msg="提成已录入")


@router.post("/salary/bill/create", response_model=ResponseModel)
def create_salary_bill(
    data: SalaryBillCreate,
    db: Session = Depends(get_db)
):
    """生成月度工资单"""
    # 验证员工
    staff = db.query(Staff).filter(Staff.id == data.staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    # 检查是否已生成
    existing = db.query(SalaryBill).filter(
        SalaryBill.staff_id == data.staff_id,
        SalaryBill.month == data.month
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="该月份工资单已生成")
    
    # 计算各项
    # 人天提成合计
    day_commission_total = db.query(func.sum(StaffCommission.day_commission_amount)).filter(
        StaffCommission.staff_id == data.staff_id,
        StaffCommission.settle_status == StaffCommission.SettleStatus.PENDING,
        func.date_format(StaffCommission.create_time, "%Y-%m") == data.month
    ).scalar() or 0
    
    # 整包奖金合计
    package_bonus_total = db.query(func.sum(StaffCommission.package_bonus_amount)).filter(
        StaffCommission.staff_id == data.staff_id,
        StaffCommission.settle_status == StaffCommission.SettleStatus.PENDING,
        func.date_format(StaffCommission.create_time, "%Y-%m") == data.month
    ).scalar() or 0
    
    # 提成合计
    commission_total = float(day_commission_total) + float(package_bonus_total)
    
    # 报销合计（普通报销）
    reimburse_total = db.query(func.sum(StaffCommission.total_commission)).join(
        Project, StaffCommission.project_id == Project.id
    ).filter(
        StaffCommission.staff_id == data.staff_id,
        StaffCommission.settle_status == StaffCommission.SettleStatus.PENDING,
        func.date_format(StaffCommission.create_time, "%Y-%m") == data.month
    ).scalar() or 0
    
    # 最终薪资
    final_salary = float(staff.base_salary or 0) + commission_total + float(reimburse_total)
    
    # 创建工资单
    salary_bill = SalaryBill(
        staff_id=data.staff_id,
        month=data.month,
        base_salary_total=float(staff.base_salary or 0),
        day_commission_total=float(day_commission_total),
        package_bonus_total=float(package_bonus_total),
        commission_total=commission_total,
        reimburse_total=reimburse_total,
        final_salary=final_salary,
        status=SalaryBill.SalaryBillStatus.DRAFT
    )
    db.add(salary_bill)
    db.commit()
    db.refresh(salary_bill)
    
    return ResponseModel(data={"id": salary_bill.id}, msg="工资单已生成")