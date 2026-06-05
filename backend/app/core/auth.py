from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expire_minutes: Optional[int] = None) -> str:
    """创建JWT Token"""
    if expire_minutes is None:
        expire_minutes = settings.JWT_EXPIRE_MINUTES
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """解码JWT Token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """获取当前用户（依赖注入）"""
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id = payload.get("user_id")
    username = payload.get("username")
    
    if user_id is None or username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效",
        )
    
    return {
        "user_id": user_id,
        "username": username,
        "staff_id": payload.get("staff_id")
    }


# 简单模拟用户（实际应从数据库读取）
MOCK_USERS = {
    "admin": {
        "user_id": 1,
        "username": "admin",
        "password_hash": get_password_hash("admin123"),
        "staff_id": None
    }
}


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """验证用户登录"""
    user = MOCK_USERS.get(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user