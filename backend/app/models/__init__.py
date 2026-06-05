from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, DECIMAL, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ProjectType(str, enum.Enum):
    DAY_PROJECT = "day_project"       # 人天项目
    PACKAGE_PROJECT = "package_project"  # 整包项目


class SurplusStatus(str, enum.Enum):
    PENDING = "pending"   # 待兑付
    FINISHED = "finished"  # 已兑付
    CANCEL = "cancel"      # 作废


class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"


class RiskStatus(str, enum.Enum):
    NORMAL = "normal"     # 正常
    WARNING = "warning"   # 预警
    LOSS = "loss"         # 亏损


class StaffLevel(str, enum.Enum):
    P0 = "p0"
    P1_1 = "p1-1"
    P1_2 = "p1-2"
    P1_3 = "p1-3"


class StaffStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    RESIGNED = "resigned"


class SignStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class ReimburseType(str, enum.Enum):
    DEFAULT = "default"      # 普通报销
    DEDUCTION = "deduction"  # 抵税抵扣


class CheckStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SettleStatus(str, enum.Enum):
    PENDING = "pending"
    SETTLED = "settled"
    CANCELLED = "cancelled"


class CommissionType(str, enum.Enum):
    DAY = "day"                    # 仅人天提成
    BOTH = "both"                 # 人天+整包奖金
    PACKAGE = "package"           # 单独奖金（预留）


class SalaryBillStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    PAID = "paid"


class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String(200), nullable=False, comment="项目名称")
    customer_project_name = Column(String(200), nullable=True, comment="客户内部项目名")
    customer_project_code = Column(String(100), nullable=True, comment="客户内部项目编号")
    company_name = Column(String(200), nullable=True, comment="公司名称")
    address = Column(String(500), nullable=True, comment="项目地址")
    lng = Column(DECIMAL(10, 6), nullable=True, comment="经度")
    lat = Column(DECIMAL(10, 6), nullable=True, comment="纬度")
    contract_amount = Column(DECIMAL(15, 2), nullable=True, comment="合同金额")
    payment_term = Column(String(200), nullable=True, comment="付款周期")
    project_type = Column(Enum(ProjectType), nullable=False, comment="项目类型")
    fixed_package_amount = Column(DECIMAL(15, 2), nullable=True, comment="固定包干总价")
    customer_surplus_man_day = Column(Integer, default=0, comment="客户溢量人天")
    surplus_man_day_status = Column(Enum(SurplusStatus), default=SurplusStatus.PENDING, comment="溢量兑付状态")
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE, comment="项目状态")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # Relationships
    contract_payments = relationship("ContractPayment", back_populates="project", cascade="all, delete-orphan")
    project_staff_configs = relationship("ProjectStaffConfig", back_populates="project", cascade="all, delete-orphan")
    sign_records = relationship("SignRecord", back_populates="project", cascade="all, delete-orphan")
    reimburses = relationship("Reimburse", back_populates="project", cascade="all, delete-orphan")
    staff_commissions = relationship("StaffCommission", back_populates="project", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_project_type", "project_type"),
        Index("idx_project_status", "status"),
        Index("idx_project_name", "project_name"),
    )


class ContractPayment(Base):
    __tablename__ = "contract_payment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False, comment="项目ID")
    contract_no = Column(String(100), nullable=False, unique=True, comment="合同编号")
    total_amount = Column(DECIMAL(15, 2), default=0, comment="合同总金额")
    paid_amount = Column(DECIMAL(15, 2), default=0, comment="已回款金额")
    unpaid_amount = Column(DECIMAL(15, 2), default=0, comment="未回款金额")
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.UNPAID, comment="回款状态")
    expect_pay_date = Column(DateTime, nullable=True, comment="预计回款日期")
    last_mail_check_time = Column(DateTime, nullable=True, comment="最近邮件核查时间")
    project_surplus_income = Column(DECIMAL(15, 2), default=0, comment="溢量过路流水营收")
    project_cost_man_day = Column(DECIMAL(15, 2), default=0, comment="项目人力总成本")
    project_cost_travel = Column(DECIMAL(15, 2), default=0, comment="项目差旅总成本")
    project_gross_profit = Column(DECIMAL(15, 2), default=0, comment="项目毛利")
    package_cost_budget = Column(DECIMAL(15, 2), nullable=True, comment="整包成本预算")
    package_cost_surplus = Column(DECIMAL(15, 2), nullable=True, comment="整包成本剩余")
    package_risk_status = Column(Enum(RiskStatus), default=RiskStatus.NORMAL, comment="整包风险状态")

    # Relationships
    project = relationship("Project", back_populates="contract_payments")
    staff_commissions = relationship("StaffCommission", back_populates="contract_payment")

    __table_args__ = (
        Index("idx_contract_project", "project_id"),
        Index("idx_contract_no", "contract_no"),
    )


class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feishu_uid = Column(String(100), unique=True, nullable=True, comment="飞书UID")
    name = Column(String(50), nullable=False, comment="姓名")
    department = Column(String(100), nullable=True, comment="部门")
    staff_level = Column(Enum(StaffLevel), nullable=False, comment="职级")
    base_salary = Column(DECIMAL(15, 2), default=0, comment="底薪")
    default_day_price = Column(Integer, nullable=False, comment="默认对外结算单价")
    default_day_commission = Column(Integer, nullable=False, comment="默认人天提成单价")
    day_commission_rate = Column(DECIMAL(5, 4), default=0, comment="人天提成比例")
    package_commission_rate = Column(DECIMAL(5, 4), default=0, comment="整包提成比例")
    status = Column(Enum(StaffStatus), default=StaffStatus.ACTIVE, comment="状态")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # Relationships
    project_staff_configs = relationship("ProjectStaffConfig", back_populates="staff", cascade="all, delete-orphan")
    sign_records = relationship("SignRecord", back_populates="staff", cascade="all, delete-orphan")
    reimburses = relationship("Reimburse", back_populates="staff", cascade="all, delete-orphan")
    staff_commissions = relationship("StaffCommission", back_populates="staff", cascade="all, delete-orphan")
    salary_bills = relationship("SalaryBill", back_populates="staff", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_staff_level", "staff_level"),
        Index("idx_staff_status", "status"),
        Index("idx_staff_feishu", "feishu_uid"),
    )


class ProjectStaffConfig(Base):
    __tablename__ = "project_staff_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False, comment="项目ID")
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"), nullable=False, comment="员工ID")
    custom_day_commission = Column(Integer, nullable=True, comment="自定义人天提成单价")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # Relationships
    project = relationship("Project", back_populates="project_staff_configs")
    staff = relationship("Staff", back_populates="project_staff_configs")

    __table_args__ = (
        UniqueConstraint("project_id", "staff_id", name="uk_project_staff"),
        Index("idx_psc_project", "project_id"),
        Index("idx_psc_staff", "staff_id"),
    )


class SignRecord(Base):
    __tablename__ = "sign_record"

    task_id = Column(String(50), primary_key=True, comment="任务ID")
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"), nullable=False, comment="员工ID")
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False, comment="项目ID")
    sign_lng = Column(DECIMAL(10, 6), nullable=True, comment="签到经度")
    sign_lat = Column(DECIMAL(10, 6), nullable=True, comment="签到纬度")
    sign_address = Column(String(500), nullable=True, comment="签到地址")
    sign_status = Column(Enum(SignStatus), default=SignStatus.PENDING, comment="签到状态")
    screenshot_url = Column(String(500), nullable=True, comment="截图URL")
    sign_time = Column(DateTime, nullable=True, comment="签到时间")
    source = Column(String(20), nullable=False, comment="来源：feishu/web/system")

    # Relationships
    staff = relationship("Staff", back_populates="sign_records")
    project = relationship("Project", back_populates="sign_records")

    __table_args__ = (
        Index("idx_sign_staff", "staff_id"),
        Index("idx_sign_project", "project_id"),
        Index("idx_sign_time", "sign_time"),
        Index("idx_sign_status", "sign_status"),
    )


class Reimburse(Base):
    __tablename__ = "reimburse"

    id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"), nullable=False, comment="员工ID")
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False, comment="项目ID")
    invoice_no = Column(String(100), nullable=False, comment="发票号")
    invoice_amount = Column(DECIMAL(15, 2), nullable=False, comment="发票金额")
    invoice_date = Column(DateTime, nullable=True, comment="发票日期")
    file_url = Column(String(500), nullable=True, comment="文件URL")
    remark = Column(Text, nullable=True, comment="备注")
    reimburse_type = Column(Enum(ReimburseType), default=ReimburseType.DEFAULT, comment="报销类型")
    check_status = Column(Enum(CheckStatus), default=CheckStatus.PENDING, comment="审核状态")
    settle_status = Column(Enum(SettleStatus), default=SettleStatus.PENDING, comment="结算状态")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")

    # Relationships
    staff = relationship("Staff", back_populates="reimburses")
    project = relationship("Project", back_populates="reimburses")

    __table_args__ = (
        Index("idx_reimburse_staff", "staff_id"),
        Index("idx_reimburse_project", "project_id"),
        Index("idx_reimburse_type", "reimburse_type"),
        Index("idx_reimburse_settle", "settle_status"),
    )


class StaffCommission(Base):
    __tablename__ = "staff_commission"

    id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"), nullable=False, comment="员工ID")
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False, comment="项目ID")
    payment_id = Column(Integer, ForeignKey("contract_payment.id", ondelete="SET NULL"), nullable=True, comment="回款ID")
    commission_type = Column(Enum(CommissionType), nullable=False, comment="提成类型")
    day_commission_amount = Column(DECIMAL(15, 2), default=0, comment="人天提成金额")
    package_bonus_amount = Column(DECIMAL(15, 2), default=0, comment="整包奖金金额")
    total_commission = Column(DECIMAL(15, 2), default=0, comment="总提成")
    rate = Column(DECIMAL(5, 4), nullable=True, comment="提成比例")
    project_day_commission = Column(Integer, default=0, comment="项目人天数")
    settle_status = Column(Enum(SettleStatus), default=SettleStatus.PENDING, comment="结算状态")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")

    # Relationships
    staff = relationship("Staff", back_populates="staff_commissions")
    project = relationship("Project", back_populates="staff_commissions")
    contract_payment = relationship("ContractPayment", back_populates="staff_commissions")

    __table_args__ = (
        Index("idx_sc_staff", "staff_id"),
        Index("idx_sc_project", "project_id"),
        Index("idx_sc_payment", "payment_id"),
        Index("idx_sc_settle", "settle_status"),
    )


class SalaryBill(Base):
    __tablename__ = "salary_bill"

    id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"), nullable=False, comment="员工ID")
    month = Column(String(7), nullable=False, comment="月份YYYY-MM")
    base_salary_total = Column(DECIMAL(15, 2), default=0, comment="底薪合计")
    day_commission_total = Column(DECIMAL(15, 2), default=0, comment="人天提成合计")
    package_bonus_total = Column(DECIMAL(15, 2), default=0, comment="整包奖金合计")
    commission_total = Column(DECIMAL(15, 2), default=0, comment="提成合计")
    reimburse_total = Column(DECIMAL(15, 2), default=0, comment="报销合计")
    final_salary = Column(DECIMAL(15, 2), default=0, comment="最终薪资")
    status = Column(Enum(SalaryBillStatus), default=SalaryBillStatus.DRAFT, comment="状态")
    file_url = Column(String(500), nullable=True, comment="工资单文件URL")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")

    # Relationships
    staff = relationship("Staff", back_populates="salary_bills")

    __table_args__ = (
        UniqueConstraint("staff_id", "month", name="uk_staff_month"),
        Index("idx_sb_staff", "staff_id"),
        Index("idx_sb_month", "month"),
        Index("idx_sb_status", "status"),
    )