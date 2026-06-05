from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============ 通用响应结构 ============
class ResponseModel(BaseModel):
    code: int = 0
    msg: str = "success"
    data: Optional[dict] = None


class ListResponse(BaseModel):
    code: int = 0
    msg: str = "success"
    data: Optional[dict] = None
    total: Optional[int] = None


# ============ 枚举定义 ============
class ProjectType(str, Enum):
    DAY_PROJECT = "day_project"
    PACKAGE_PROJECT = "package_project"


class SurplusStatus(str, Enum):
    PENDING = "pending"
    FINISHED = "finished"
    CANCEL = "cancel"


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class StaffLevel(str, Enum):
    P0 = "p0"
    P1_1 = "p1-1"
    P1_2 = "p1-2"
    P1_3 = "p1-3"


class ReimburseType(str, Enum):
    DEFAULT = "default"
    DEDUCTION = "deduction"


class SignStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


# ============ 项目相关 ============
class ProjectCreate(BaseModel):
    project_name: str = Field(..., max_length=200)
    customer_project_name: Optional[str] = Field(None, max_length=200)
    customer_project_code: Optional[str] = Field(None, max_length=100)
    company_name: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    lng: Optional[float] = None
    lat: Optional[float] = None
    contract_amount: Optional[float] = None
    payment_term: Optional[str] = Field(None, max_length=200)
    project_type: ProjectType
    fixed_package_amount: Optional[float] = None
    status: ProjectStatus = ProjectStatus.ACTIVE


class ProjectUpdate(BaseModel):
    id: int
    project_name: Optional[str] = Field(None, max_length=200)
    customer_project_name: Optional[str] = Field(None, max_length=200)
    customer_project_code: Optional[str] = Field(None, max_length=100)
    company_name: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    lng: Optional[float] = None
    lat: Optional[float] = None
    contract_amount: Optional[float] = None
    payment_term: Optional[str] = Field(None, max_length=200)
    project_type: Optional[ProjectType] = None
    fixed_package_amount: Optional[float] = None
    customer_surplus_man_day: Optional[int] = None
    surplus_man_day_status: Optional[SurplusStatus] = None
    status: Optional[ProjectStatus] = None


class ProjectStaffConfigSave(BaseModel):
    project_id: int
    staff_id: int
    custom_day_commission: Optional[int] = None


class ProjectProfitResponse(BaseModel):
    project_id: int
    project_type: str
    project_name: str
    real_revenue: float = 0  # 真实营收
    real_cost_man_day: float = 0  # 人力成本
    real_cost_travel: float = 0  # 差旅成本
    real_gross_profit: float = 0  # 真实毛利
    surplus_man_day: int = 0  # 溢量人天
    surplus_income: float = 0  # 溢量营收
    surplus_status: str = "pending"  # 溢量状态
    # 整包特有
    fixed_package_amount: Optional[float] = None
    package_cost_budget: Optional[float] = None
    package_cost_surplus: Optional[float] = None
    package_risk_status: Optional[str] = None


# ============ 合同回款相关 ============
class ContractPaymentUpdate(BaseModel):
    id: int
    paid_amount: Optional[float] = None
    payment_status: Optional[str] = None
    expect_pay_date: Optional[datetime] = None


# ============ 员工相关 ============
class StaffCreate(BaseModel):
    feishu_uid: Optional[str] = Field(None, max_length=100)
    name: str = Field(..., max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    staff_level: StaffLevel
    base_salary: Optional[float] = 0
    default_day_price: int
    default_day_commission: int
    day_commission_rate: Optional[float] = 0
    package_commission_rate: Optional[float] = 0


class StaffUpdate(BaseModel):
    id: int
    feishu_uid: Optional[str] = Field(None, max_length=100)
    name: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    staff_level: Optional[StaffLevel] = None
    base_salary: Optional[float] = None
    default_day_price: Optional[int] = None
    default_day_commission: Optional[int] = None
    day_commission_rate: Optional[float] = None
    package_commission_rate: Optional[float] = None
    status: Optional[str] = None


# ============ 签到相关 ============
class SignTaskCreate(BaseModel):
    staff_id: int
    project_id: int
    sign_lng: Optional[float] = None
    sign_lat: Optional[float] = None
    sign_address: Optional[str] = Field(None, max_length=500)
    source: str = "web"  # feishu/web/system


class SignResultSave(BaseModel):
    task_id: str
    sign_status: SignStatus
    sign_lng: Optional[float] = None
    sign_lat: Optional[float] = None
    sign_address: Optional[str] = Field(None, max_length=500)
    screenshot_url: Optional[str] = Field(None, max_length=500)
    sign_time: Optional[datetime] = None
    msg: Optional[str] = None


# ============ 报销相关 ============
class ReimburseCreate(BaseModel):
    staff_id: int
    project_id: int
    invoice_no: str = Field(..., max_length=100)
    invoice_amount: float
    invoice_date: Optional[datetime] = None
    file_url: Optional[str] = Field(None, max_length=500)
    remark: Optional[str] = None
    reimburse_type: ReimburseType = ReimburseType.DEFAULT


class ReimburseStaffMonthResponse(BaseModel):
    staff_id: int
    staff_name: str
    month: str
    reimburse_type: str
    total_amount: float
    count: int


# ============ 提成薪资相关 ============
class CommissionAdd(BaseModel):
    staff_id: int
    project_id: int
    payment_id: Optional[int] = None
    commission_type: str  # day/both/package
    day_commission_amount: Optional[float] = 0
    package_bonus_amount: Optional[float] = 0
    project_day_commission: int = 0  # 项目人天数


class SalaryBillCreate(BaseModel):
    staff_id: int
    month: str = Field(..., pattern=r"^\d{4}-\d{2}$")


# ============ 任务调度相关 ============
class TaskRetry(BaseModel):
    task_id: str
    task_type: str  # sign/ocr/payment/salary


class DeadTaskResponse(BaseModel):
    task_id: str
    task_type: str
    source: str
    create_time: str
    payload: dict
    error_msg: str
    retry_count: int


# ============ 认证相关 ============
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUser(BaseModel):
    user_id: int
    username: str
    staff_id: Optional[int] = None