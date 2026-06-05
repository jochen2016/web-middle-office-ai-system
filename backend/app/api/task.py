from fastapi import APIRouter, Depends
from app.services.redis_service import redis_queue
from app.schemas import TaskRetry, DeadTaskResponse, ResponseModel, ListResponse
from app.config import get_settings
import json

router = APIRouter(prefix="/task", tags=["任务调度"])
settings = get_settings()


@router.get("/dead/list", response_model=ListResponse)
def get_dead_task_list(
    task_type: str = None,
    page: int = 1,
    page_size: int = 20
):
    """查询死信任务"""
    dead_tasks = redis_queue.peek(settings.QUEUE_DEAD_TASK, count=100)
    
    filtered_tasks = dead_tasks
    if task_type:
        filtered_tasks = [t for t in dead_tasks if t.get("task_type") == task_type]
    
    total = len(filtered_tasks)
    offset = (page - 1) * page_size
    page_tasks = filtered_tasks[offset:offset + page_size]
    
    task_list = []
    for t in page_tasks:
        task_list.append({
            "task_id": t.get("task_id"),
            "task_type": t.get("task_type"),
            "source": t.get("source"),
            "create_time": t.get("create_time"),
            "payload": t.get("payload", {}),
            "error_msg": t.get("error_msg", ""),
            "retry_count": t.get("retry_count", 0),
        })
    
    return ListResponse(data={"list": task_list}, total=total)


@router.post("/retry", response_model=ResponseModel)
def retry_dead_task(
    data: TaskRetry
):
    """手动重跑失败任务"""
    # 从死信队列获取任务
    dead_tasks = redis_queue.peek(settings.QUEUE_DEAD_TASK, count=100)
    
    target_task = None
    for t in dead_tasks:
        if t.get("task_id") == data.task_id:
            target_task = t
            break
    
    if not target_task:
        return ResponseModel(code=404, msg="任务不存在")
    
    # 更新重试次数
    target_task["retry_count"] = target_task.get("retry_count", 0) + 1
    
    # 根据任务类型重新入队
    queue_map = {
        "sign": settings.QUEUE_SIGN_SUBMIT,
        "ocr": settings.QUEUE_REIMBURSE_OCR,
        "payment": settings.QUEUE_PAYMENT_MAIL,
        "salary": settings.QUEUE_SALARY_CALC,
    }
    
    queue_name = queue_map.get(data.task_type)
    if not queue_name:
        return ResponseModel(code=400, msg="未知的任务类型")
    
    success = redis_queue.enqueue(queue_name, target_task)
    
    if success:
        return ResponseModel(msg="任务已重新入队")
    else:
        return ResponseModel(code=500, msg="重试失败")