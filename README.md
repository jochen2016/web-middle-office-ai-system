# Web中台AI系统

> 人天整包双模式精准利润核算中台

## 系统定位

Web为系统唯一数据读写入口、唯一任务调度中心，飞书、Web后台、AI Agent三端数据统一归一。

- **Web中台**：账号权限、参数校验、数据CRUD、队列生产、定时调度、结果回调消费、日志记录、业务核算
- **AI Agent**：仅执行自动化动作（签到、OCR识别、邮件解析、薪资运算），不读库、不写库、不修改配置

## 技术栈

| 模块 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy + MySQL |
| 队列/缓存 | Redis |
| 认证 | JWT |
| 前端 | Vue3 + Element Plus + Vite |
| 数据库 | MySQL 8.0+ |

## 项目模式

- **人天项目(day_project)**：营收=在岗人天×对外结算单价，按月递增，无封顶
- **整包项目(package_project)**：营收=固定包干总价，需成本风控

## 员工职级定价

| 职级 | 对外结算单价 | 员工提成单价 |
|------|------------|------------|
| p0 | 600 | 50 |
| p1-1 | 800 | 120 |
| p1-2 | 1000 | 220 |
| p1-3 | 1200 | 300 |

## 数据库8张表

1. `project` - 项目表
2. `contract_payment` - 合同回款表
3. `staff` - 员工档案表
4. `project_staff_config` - 项目人员提成配置表
5. `sign_record` - 签到记录表
6. `reimburse` - 报销明细表
7. `staff_commission` - 项目提成表
8. `salary_bill` - 工资单表

## Redis队列

| 队列 | 用途 |
|------|------|
| queue:sign:submit | 签到任务 |
| queue:reimburse:ocr | OCR识别任务 |
| queue:payment:mail | 邮件解析任务 |
| queue:salary:calc | 薪资核算任务 |
| queue:callback:result | 回调结果队列 |
| queue:dead:task | 死信队列 |

## 快速启动

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## API前缀

所有接口统一前缀：`/api/v1`

## License

MIT