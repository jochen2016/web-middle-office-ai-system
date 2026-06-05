from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SignRecord, Project, Staff
from app.schemas import SignTaskCreate, SignResultSave, ResponseModel, ListResponse
from app.services.redis_service import redis_queue
from app.config import get_settings
import uuid
from datetime import datetime

router = APIRouter(prefix="/sign", tags=["签到管理"])
settings = get_settings()


@router.post("/task/create", response_model=ResponseModel)
def create_sign_task(
    data: SignTaskCreate,
    db: Session = Depends(get_db)
):
    """创建签到任务入队"""
    # 验证员工和项目存在
    staff = db.query(Staff).filter(Staff.id == data.staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 生成任务ID
    task_id = f"sign_{uuid.uuid4().hex[:16]}"
    
    # 构建任务数据
    task_data = {
        "task_id": task_id,
        "task_type": "sign",
        "source": data.source,
        "create_time": datetime.now().isoformat(),
        "payload": {
            "staff_id": data.staff_id,
            "project_id": data.project_id,
            "sign_lng": data.sign_lng,
            "sign_lat": data.sign_lat,
            "sign_address": data.sign_address,
        },
        "retry_count": 0
    }
    
    # 入队
    success = redis_queue.enqueue(settings.QUEUE_SIGN_SUBMIT, task_data)
    if not success:
        raise HTTPException(status_code=500, detail="任务入队失败")
    
    return ResponseModel(data={"task_id": task_id}, msg="任务已入队")


@router.post("/result/save", response_model=ResponseModel)
def save_sign_result(
    data: SignResultSave,
    db: Session = Depends(get_db)
):
    """接收Agent签到结果入库"""
    sign_record = db.query(SignRecord).filter(SignRecord.task_id == data.task_id).first()
    
    if not sign_record:
        # 新建记录
        payload = {}  # 从回调中获取
        sign_record = SignRecord(
            task_id=data.task_id,
            staff_id=payload.get("staff_id", 0),
            project_id=payload.get("project_id", 0),
            sign_status=data.sign_status,
            sign_lng=data.sign_lng,
            sign_lat=data.sign_lat,
            sign_address=data.sign_address,
            screenshot_url=data.screenshot_url,
            sign_time=data.sign_time,
            source=payload.get("source", "web")
        )
        db.add(sign_record)
    else:
        sign_record.sign_status = data.sign_status
        sign_record.sign_lng = data.sign_lng
        sign_record.sign_lat = data.sign_lat
        sign_record.sign_address = data.sign_address
        sign_record.screenshot_url = data.screenshot_url
        sign_record.sign_time = data.sign_time
    
    db.commit()
    
    return ResponseModel(msg="签到结果已保存")


@router.get("/list", response_model=ListResponse)
def get_sign_list(
    staff_id: int = None,
    project_id: int = None,
    sign_status: str = None,
    start_date: str = None,
    end_date: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """查询签到记录"""
    query = db.query(SignRecord)
    
    if staff_id:
        query = query.filter(SignRecord.staff_id == staff_id)
    if project_id:
        query = query.filter(SignRecord.project_id == project_id)
    if sign_status:
        query = query.filter(SignRecord.sign_status == sign_status)
    if start_date:
        query = query.filter(SignRecord.sign_time >= start_date)
    if end_date:
        query = query.filter(SignRecord.sign_time <= end_date)
    
    total = query.count()
    offset = (page - 1) * page_size
    records = query.order_by(SignRecord.sign_time.desc()).offset(offset).limit(page_size).all()
    
    sign_list = []
    for r in records:
        staff = db.query(Staff).filter(Staff.id == r.staff_id).first()
        project = db.query(Project).filter(Project.id == r.project_id).first()
        sign_list.append({
            "task_id": r.task_id,
            "staff_id": r.staff_id,
            "staff_name": staff.name if staff else None,
            "project_id": r.project_id,
            "project_name": project.project_name if project else None,
            "sign_lng": float(r.sign_lng) if r.sign_lng else None,
            "sign_lat": float(r.sign_lat) if r.sign_lat else None,
            "sign_address": r.sign_address,
            "sign_status": r.sign_status.value if r.sign_status else None,
            "screenshot_url": r.screenshot_url,
            "sign_time": r.sign_time.isoformat() if r.sign_time else None,
            "source": r.source,
        })
    
    return ListResponse(data={"list": sign_list}, total=total)