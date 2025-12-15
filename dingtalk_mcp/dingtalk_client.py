"""
钉钉开放平台 API 客户端

负责管理 access_token、调用钉钉文档相关 API，并处理错误。
"""

import time
import logging
from typing import Optional, Dict, Any
import httpx

from .config import DingTalkConfig


class DingTalkAPIError(Exception):
    """钉钉 API 调用异常"""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details


# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DingTalkClient:
    """
    钉钉客户端，负责管理 access_token 和调用钉钉 API。
    
    Attributes:
        config: 钉钉配置对象
        _access_token: 当前 access_token
        _token_expires_at: token 过期时间戳
    """
    
    def __init__(self, config: DingTalkConfig):
        self.config = config
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._http_client = httpx.Client(timeout=30.0)
    
    def _is_token_expired(self) -> bool:
        """检查 token 是否已过期（提前 5 分钟刷新）"""
        return time.time() >= (self._token_expires_at - 300)
    
    def _request_access_token(self) -> str:
        """
        向钉钉开放平台请求新的 access_token。
        
        Returns:
            str: 新的 access_token
            
        Raises:
            DingTalkAPIError: 如果请求失败
        """
        url = f"{self.config.base_url}/v1.0/oauth2/accessToken"
        max_retries = 3
        retry_delay = 1  # 初始重试延迟为 1 秒
        
        for retry_count in range(max_retries):
            try:
                logger.info(f"请求 access_token，URL: {url}，重试次数: {retry_count + 1}")
                response = self._http_client.post(
                    url,
                    json={
                        "appKey": self.config.app_key,
                        "appSecret": self.config.app_secret,
                    },
                )
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"获取 access_token 成功，响应: {data}")
                
                if "accessToken" not in data:
                    logger.error(f"获取 access_token 失败：响应中缺少 accessToken，响应: {data}")
                    if retry_count < max_retries - 1:
                        logger.info(f"将在 {retry_delay} 秒后重试...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                        continue
                    else:
                        raise DingTalkAPIError(
                            message="获取 access_token 失败：响应中缺少 accessToken",
                            code="TOKEN_MISSING",
                            details=str(data),
                        )
                
                return data["accessToken"]
                
            except httpx.HTTPError as e:
                if retry_count < max_retries - 1:
                    logger.info(f"HTTP 请求错误，将在 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    logger.error(f"获取 access_token 失败：HTTP 请求错误")
                    raise DingTalkAPIError(
                        message=f"获取 access_token 失败：HTTP 请求错误",
                        code="HTTP_ERROR",
                        details=str(e),
                    )
            
            except Exception as e:
                if retry_count < max_retries - 1:
                    logger.info(f"未知错误，将在 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    logger.error(f"获取 access_token 失败：未知错误")
                    raise DingTalkAPIError(
                        message=f"获取 access_token 失败：未知错误",
                        code="UNKNOWN_ERROR",
                        details=str(e),
                    )
    
    def get_access_token(self) -> str:
        """
        获取有效的 access_token，如果已过期则自动刷新。
        
        Returns:
            str: 有效的 access_token
            
        Raises:
            DingTalkAPIError: 如果获取 token 失败
        """
        if not self._access_token or self._is_token_expired():
            try:
                self._access_token = self._request_access_token()
                # 设置过期时间（钉钉 token 默认 7200 秒）
                self._token_expires_at = time.time() + self.config.token_cache_ttl
            except DingTalkAPIError:
                # 如果刷新失败，清除现有 token 并重新抛出异常
                self._access_token = None
                self._token_expires_at = 0
                raise
        
        return self._access_token
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求到钉钉 API。
        
        Args:
            method: HTTP 方法（GET、POST、PUT 等）
            endpoint: API 端点（不包含基础 URL）
            params: URL 查询参数
            json: JSON 请求体
            
        Returns:
            Dict[str, Any]: API 响应数据
            
        Raises:
            DingTalkAPIError: 如果请求失败
        """
        url = f"{self.config.base_url}{endpoint}"
        headers = {
            "x-acs-dingtalk-access-token": self.get_access_token(),
            "Content-Type": "application/json",
        }
        
        # 日志记录请求信息，不记录完整 token
        logged_headers = headers.copy()
        logged_headers["x-acs-dingtalk-access-token"] = logged_headers["x-acs-dingtalk-access-token"][:20] + "..." if logged_headers["x-acs-dingtalk-access-token"] else ""
        
        try:
            logger.info(f"发送 {method} 请求到 URL: {url}, params: {params}, json: {json}")
            response = self._http_client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"API 请求成功，URL: {url}, 响应: {data}")
            
            # 检查业务错误码
            if isinstance(data, dict):
                error_code = data.get("errcode")
                if error_code and error_code != 0:
                    logger.error(f"API 请求业务错误，URL: {url}, 错误: {data}")
                    raise DingTalkAPIError(
                        message=data.get("errmsg", "未知错误"),
                        code=str(error_code),
                        details=str(data),
                    )
            
            return data
        except httpx.HTTPError as e:
            logger.error(f"API 请求 HTTP 错误，URL: {url}, 错误: {str(e)}")
            raise DingTalkAPIError(
                message=f"API 请求失败：HTTP 错误",
                code="HTTP_ERROR",
                details=str(e),
            )
        except Exception as e:
            logger.error(f"API 请求未知错误，URL: {url}, 错误: {str(e)}")
            raise DingTalkAPIError(
                message=f"API 请求失败：未知错误",
                code="UNKNOWN_ERROR",
                details=str(e),
            )
    
    def create_document(
        self,
        title: str,
        content: Optional[str] = None,
        space_id: Optional[str] = None,
        folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        创建钉钉文档。
        
        Args:
            title: 文档标题
            content: 文档初始内容
            space_id: 空间 ID
            folder_id: 文件夹 ID
            
        Returns:
            Dict[str, Any]: 包含文档 ID、标题、创建时间等信息
            
        Raises:
            DingTalkAPIError: 如果创建失败
        """
        request_data = {"title": title}
        
        if content is not None:
            request_data["content"] = content
        if space_id is not None:
            request_data["spaceId"] = space_id
        if folder_id is not None:
            request_data["folderId"] = folder_id
        
        response = self._make_request("POST", "/v1.0/doc/documents", json=request_data)
        
        return {
            "success": True,
            "document_id": response.get("docId") or response.get("documentId"),
            "title": title,
            "create_time": response.get("createTime"),
            "url": response.get("url"),
        }
    
    def get_document(self, document_id: str, format: str = "text") -> Dict[str, Any]:
        """
        获取文档内容。
        
        Args:
            document_id: 文档 ID
            format: 返回格式（text/markdown/html）
            
        Returns:
            Dict[str, Any]: 包含文档内容、标题、格式等信息
            
        Raises:
            DingTalkAPIError: 如果获取失败
        """
        params = {"format": format}
        response = self._make_request(
            "GET", f"/v1.0/doc/documents/{document_id}", params=params
        )
        
        return {
            "success": True,
            "document_id": document_id,
            "title": response.get("title"),
            "content": response.get("content"),
            "format": format,
            "update_time": response.get("updateTime"),
            "author": response.get("author"),
        }
    
    def update_document(
        self,
        document_id: str,
        content: str,
        mode: str = "overwrite",
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        更新文档内容。
        
        Args:
            document_id: 文档 ID
            content: 更新内容
            mode: 更新模式（overwrite/append）
            comment: 更新备注
            
        Returns:
            Dict[str, Any]: 包含更新状态、更新时间、版本号等信息
            
        Raises:
            DingTalkAPIError: 如果更新失败
        """
        request_data = {"content": content, "mode": mode}
        
        if comment is not None:
            request_data["comment"] = comment
        
        response = self._make_request(
            "PUT", f"/v1.0/doc/documents/{document_id}", json=request_data
        )
        
        return {
            "success": True,
            "document_id": document_id,
            "update_time": response.get("updateTime"),
            "version": response.get("version"),
        }
    
    def list_documents(
        self,
        space_id: Optional[str] = None,
        folder_id: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "update_time",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """
        列出可访问的文档。
        
        Args:
            space_id: 空间 ID
            folder_id: 文件夹 ID
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            sort_by: 排序字段
            sort_order: 排序顺序
            
        Returns:
            Dict[str, Any]: 包含文档列表和分页信息
            
        Raises:
            DingTalkAPIError: 如果查询失败
        """
        params = {
            "page": page,
            "pageSize": page_size,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }
        
        if space_id is not None:
            params["spaceId"] = space_id
        if folder_id is not None:
            params["folderId"] = folder_id
        if keyword is not None:
            params["keyword"] = keyword
        
        response = self._make_request("GET", "/v1.0/doc/documents", params=params)
        
        documents = []
        for doc in response.get("documents", []):
            documents.append({
                "document_id": doc.get("docId") or doc.get("documentId"),
                "title": doc.get("title"),
                "summary": doc.get("summary"),
                "create_time": doc.get("createTime"),
                "update_time": doc.get("updateTime"),
                "author": doc.get("author"),
                "space_id": doc.get("spaceId"),
                "folder_id": doc.get("folderId"),
            })
        
        pagination = response.get("pagination", {})
        return {
            "success": True,
            "documents": documents,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": pagination.get("total", 0),
                "total_pages": pagination.get("totalPages", 0),
            },
        }