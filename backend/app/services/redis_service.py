import redis
import json
from typing import Optional, Dict, Any
from app.config import get_settings

settings = get_settings()


class RedisQueue:
    """Redis队列服务"""
    
    def __init__(self):
        self._pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
        self._client = redis.Redis(connection_pool=self._pool)
    
    @property
    def client(self) -> redis.Redis:
        return self._client
    
    def enqueue(self, queue_name: str, task_data: Dict[str, Any]) -> bool:
        """入队"""
        try:
            task_data["enqueue_time"] = str(int(__import__("time").time()))
            self._client.rpush(queue_name, json.dumps(task_data, ensure_ascii=False))
            return True
        except Exception as e:
            print(f"入队失败: {e}")
            return False
    
    def dequeue(self, queue_name: str, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """出队（阻塞）"""
        try:
            result = self._client.blpop(queue_name, timeout=timeout)
            if result:
                _, data = result
                return json.loads(data)
            return None
        except Exception as e:
            print(f"出队失败: {e}")
            return None
    
    def brpoplpush(self, queue_source: str, queue_dest: str, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """阻塞式转移（用于死信队列）"""
        try:
            result = self._client.brpoplpush(queue_source, queue_dest, timeout=timeout)
            if result:
                return json.loads(result)
            return None
        except Exception as e:
            print(f"转移失败: {e}")
            return None
    
    def get_queue_length(self, queue_name: str) -> int:
        """获取队列长度"""
        return self._client.llen(queue_name)
    
    def peek(self, queue_name: str, count: int = 10) -> list:
        """查看队列内容（不删除）"""
        try:
            items = self._client.lrange(queue_name, 0, count - 1)
            return [json.loads(item) for item in items]
        except Exception:
            return []
    
    def move_to_dead(self, task_data: Dict[str, Any], error_msg: str = "") -> bool:
        """任务移至死信队列"""
        try:
            task_data["error_msg"] = error_msg
            task_data["dead_time"] = str(int(__import__("time").time()))
            self._client.rpush(settings.QUEUE_DEAD_TASK, json.dumps(task_data, ensure_ascii=False))
            return True
        except Exception as e:
            print(f"死信入队失败: {e}")
            return False


class RedisCache:
    """Redis缓存服务"""
    
    def __init__(self):
        self._pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
        self._client = redis.Redis(connection_pool=self._pool)
    
    def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """设置缓存"""
        try:
            self._client.setex(key, expire, value)
            return True
        except Exception as e:
            print(f"缓存设置失败: {e}")
            return False
    
    def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        try:
            return self._client.get(key)
        except Exception:
            return None
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            self._client.delete(key)
            return True
        except Exception:
            return False


# 全局实例
redis_queue = RedisQueue()
redis_cache = RedisCache()