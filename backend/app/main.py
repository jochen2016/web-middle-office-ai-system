from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db, init_db
from app.config import get_settings
from app.core.auth import authenticate_user, create_access_token
from app.schemas import LoginRequest, TokenResponse, ResponseModel

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
@app.on_event("startup")
def startup():
    init_db()


# ============ 认证接口 ============
@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(data: LoginRequest):
    """用户登录"""
    user = authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    access_token = create_access_token({
        "user_id": user["user_id"],
        "username": user["username"],
        "staff_id": user.get("staff_id")
    })
    
    return TokenResponse(access_token=access_token)


# ============ 注册路由 ============
from app.api import project, contract, sign, reimburse, salary, task, staff


@app.get("/")
def root():
    return {"message": "Web中台AI系统 API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# 注册子路由
app.include_router(project.router, prefix="/api/v1")
app.include_router(contract.router, prefix="/api/v1")
app.include_router(sign.router, prefix="/api/v1")
app.include_router(reimburse.router, prefix="/api/v1")
app.include_router(salary.router, prefix="/api/v1")
app.include_router(task.router, prefix="/api/v1")
app.include_router(staff.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)