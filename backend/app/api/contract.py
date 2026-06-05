from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ContractPayment, Project
from app.schemas import ContractPaymentUpdate, ResponseModel, ListResponse

router = APIRouter(prefix="/contract", tags=["合同回款"])


@router.get("/list", response_model=ListResponse)
def get_contract_list(
    project_id: int = None,
    payment_status: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """查询合同回款列表"""
    query = db.query(ContractPayment)
    
    if project_id:
        query = query.filter(ContractPayment.project_id == project_id)
    if payment_status:
        query = query.filter(ContractPayment.payment_status == payment_status)
    
    total = query.count()
    offset = (page - 1) * page_size
    contracts = query.order_by(ContractPayment.id.desc()).offset(offset).limit(page_size).all()
    
    contract_list = []
    for c in contracts:
        project = db.query(Project).filter(Project.id == c.project_id).first()
        contract_list.append({
            "id": c.id,
            "project_id": c.project_id,
            "project_name": project.project_name if project else None,
            "contract_no": c.contract_no,
            "total_amount": float(c.total_amount) if c.total_amount else 0,
            "paid_amount": float(c.paid_amount) if c.paid_amount else 0,
            "unpaid_amount": float(c.unpaid_amount) if c.unpaid_amount else 0,
            "payment_status": c.payment_status.value if c.payment_status else None,
            "expect_pay_date": c.expect_pay_date.isoformat() if c.expect_pay_date else None,
            "project_surplus_income": float(c.project_surplus_income) if c.project_surplus_income else 0,
            "project_cost_man_day": float(c.project_cost_man_day) if c.project_cost_man_day else 0,
            "project_cost_travel": float(c.project_cost_travel) if c.project_cost_travel else 0,
            "project_gross_profit": float(c.project_gross_profit) if c.project_gross_profit else 0,
            "package_cost_budget": float(c.package_cost_budget) if c.package_cost_budget else None,
            "package_cost_surplus": float(c.package_cost_surplus) if c.package_cost_surplus else None,
            "package_risk_status": c.package_risk_status.value if c.package_risk_status else None,
        })
    
    return ListResponse(data={"list": contract_list}, total=total)


@router.put("/payment/update", response_model=ResponseModel)
def update_contract_payment(
    data: ContractPaymentUpdate,
    db: Session = Depends(get_db)
):
    """更新回款，自动刷新项目利润成本"""
    contract = db.query(ContractPayment).filter(ContractPayment.id == data.id).first()
    if not contract:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="合同不存在")
    
    # 更新字段
    if data.paid_amount is not None:
        contract.paid_amount = data.paid_amount
        # 自动计算未回款金额
        if contract.total_amount:
            contract.unpaid_amount = float(contract.total_amount) - float(data.paid_amount)
            # 更新回款状态
            if contract.unpaid_amount <= 0:
                contract.payment_status = ContractPayment.PaymentStatus.PAID
            elif data.paid_amount > 0:
                contract.payment_status = ContractPayment.PaymentStatus.PARTIAL
    
    if data.payment_status:
        contract.payment_status = ContractPayment.PaymentStatus(data.payment_status)
    
    if data.expect_pay_date:
        contract.expect_pay_date = data.expect_pay_date
    
    db.commit()
    
    return ResponseModel(msg="更新成功")