"""
MaxKB 代理API - 解决CORS跨域问题
"""
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import httpx
from typing import Optional

router = APIRouter(tags=["MaxKB Proxy"])

# MaxKB 配置 - 请根据实际情况修改
MAXKB_BASE_URL = "http://192.168.1.100:8080"  # MaxKB服务地址
MAXKB_APPLICATION_ID = "your-application-id"  # MaxKB应用ID

# 创建httpx客户端
async def get_client():
    return httpx.AsyncClient(timeout=60.0)


@router.api_route("/maxkb/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_maxkb(request: Request, path: str):
    """
    代理转发请求到MaxKB服务
    这样前端就不会遇到CORS问题
    """
    # 构建目标URL
    target_url = f"{MAXKB_BASE_URL}/api/{path}"
    
    # 获取请求头
    headers = {}
    for key, value in request.headers.items():
        # 跳过一些不需要转发的头
        if key.lower() not in ['host', 'content-length', 'connection']:
            headers[key] = value
    
    # 获取查询参数
    query_params = dict(request.query_params)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 根据请求方法转发
            if request.method == "GET":
                response = await client.get(
                    target_url,
                    headers=headers,
                    params=query_params
                )
            elif request.method == "POST":
                body = await request.body()
                response = await client.post(
                    target_url,
                    headers=headers,
                    params=query_params,
                    content=body
                )
            elif request.method == "PUT":
                body = await request.body()
                response = await client.put(
                    target_url,
                    headers=headers,
                    params=query_params,
                    content=body
                )
            elif request.method == "DELETE":
                response = await client.delete(
                    target_url,
                    headers=headers,
                    params=query_params
                )
            elif request.method == "OPTIONS":
                # 处理预检请求
                return Response(
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                        "Access-Control-Allow-Headers": "*"
                    }
                )
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            # 返回响应
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={
                    "Content-Type": response.headers.get("content-type", "application/json"),
                    "Access-Control-Allow-Origin": "*"
                }
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="MaxKB服务超时")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="无法连接到MaxKB服务")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"代理请求失败: {str(e)}")


@router.get("/maxkb-config")
async def get_maxkb_config():
    """
    获取MaxKB的配置信息（前端使用）
    """
    return {
        "enabled": True,
        "applicationId": MAXKB_APPLICATION_ID,
        # iframe嵌入链接 - 根据实际的MaxKB链接修改
        "embedUrl": f"{MAXKB_BASE_URL}/ui/chat/{MAXKB_APPLICATION_ID}"
    }
