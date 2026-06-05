from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database import get_db
from app.models import Reimburse, Staff, Project, ContractPayment
from app.schemas import ReimburseCreate, ReimburseStaffMonthResponse, ResponseModel, ListResponse
from app.services.redis_service import redis_queue
from app.config import get_settings
import uuid
from datetime import datetime

router = APIRouter(prefix="/reimburse", tags=["报销管理"])
settings = get_settings()


@router.post("/create", response_model=ResponseModel)
def create_reimburse(
    data: ReimburseCreate,
    db: Session = Depends(get_db)
):
    """OCR报销新增（强制绑定项目）"""
    # 验证员工和项目存在
    staff = db.query(Staff).filter(Staff.id == data.staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 如果有文件URL，触发OCR识别任务
    if data.file_url:
        task_data = {
            "task_id": f"ocr_{uuid.uuid4().hex[:16]}",
            "task_type": "ocr",
            "source": "web",
            "create_time": datetime.now().isoformat(),
            "payload": {
                "staff_id": data.staff_id,
                "project_id": data.project_id,
                "file_url": data.file_url,
                "invoice_no": data.invoice_no,
            },
            "retry_count": 0
        }
        redis_queue.enqueue(settings.QUEUE_REIMBURSE_OCR, task_data)
    
    # 创建报销记录
    reimburse = Reimburse(
        staff_id=data.staff_id,
        project_id=data.project_id,
        invoice_no=data.invoice_no,
        invoice_amount=data.invoice_amount,
        invoice_date=data.invoice_date,
        file_url=data.file_url,
        remark=data.remark,
        reimburse_type=data.reimburse_type,
    )
    db.add(reimburse)
    db.commit()
    db.refresh(reimburse)
    
    # 如果是普通报销，更新项目差旅成本
    if data.reimburse_type == Reimburse.ReimburseType.DEFAULT:
        contract = db.query(ContractPayment).filter(
            ContractPayment.project_id == data.project_id
        ).order_by(ContractPayment.id.desc()).first()
        
        if contract:
            contract.project_cost_travel = float(contract.project_cost_travel or 0) + float(data.invoice_amount)
            db.commit()
    
    return ResponseModel(data={"id": reimburse.id}, msg="报销单已创建")


@router.get("/staff/month", response_model=ListResponse)
def get_staff_month_reimburse(
    staff_id: int,
    month: str,  # YYYY-MM
    db: Session = Depends(get_db)
):
    """月度报销汇总（自动过滤抵税数据）"""
    # 只查询普通报销（不查询抵税抵扣）
    records = db.query(Reimburse).filter(
        Reimburse.staff_id == staff_id,
        Reimburse.reimburse_type == Reimburse.ReimburseType.DEFAULT,
        func.date_format(Reimburse.invoice_date, "%Y-%m") == month,
        Reimburse.settle_status != Reimburse.SettleStatus.CANCELLED
    ).all()
    
    total_amount = sum(float(r.invoice_amount) for r in records)
    
    return ListResponse(data={
        "list": [{
            "staff_id": staff_id,
            "month": month,
            "reimburse_type": "default",
            "total_amount": total_amount,
            "count": len(records)
        }]
    })