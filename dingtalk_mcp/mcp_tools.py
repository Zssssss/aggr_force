"""
MCP 工具实现模块

将钉钉客户端功能映射为 MCP 工具，并处理错误转换。
"""

from typing import Optional
from .dingtalk_client import DingTalkClient, DingTalkAPIError


class MCPTools:
    """
    MCP 工具类，封装所有 MCP 工具函数。
    
    Attributes:
        client: 钉钉客户端实例
    """
    
    def __init__(self, client: DingTalkClient):
        self.client = client
    
    async def create_doc_tool(
        self,
        title: str,
        content: Optional[str] = None,
        space_id: Optional[str] = None,
        folder_id: Optional[str] = None,
    ) -> dict:
        """
        创建钉钉文档。
        
        Args:
            title: 文档标题
            content: 文档初始内容
            space_id: 空间 ID
            folder_id: 文件夹 ID
            
        Returns:
            dict: 包含文档 ID、标题、创建时间等信息
            
        Raises:
            将 DingTalkAPIError 转换为 MCP 工具错误
        """
        try:
            return self.client.create_document(
                title=title,
                content=content,
                space_id=space_id,
                folder_id=folder_id,
            )
        except DingTalkAPIError as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code or "DINGTALK_ERROR",
                "details": e.details,
            }
    
    async def get_doc_tool(
        self,
        document_id: str,
        format: str = "text",
    ) -> dict:
        """
        获取文档内容。
        
        Args:
            document_id: 文档 ID
            format: 返回格式（text/markdown/html）
            
        Returns:
            dict: 包含文档内容、标题、格式等信息
            
        Raises:
            将 DingTalkAPIError 转换为 MCP 工具错误
        """
        try:
            return self.client.get_document(
                document_id=document_id,
                format=format,
            )
        except DingTalkAPIError as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code or "DINGTALK_ERROR",
                "details": e.details,
            }
    
    async def update_doc_tool(
        self,
        document_id: str,
        content: str,
        mode: str = "overwrite",
        comment: Optional[str] = None,
    ) -> dict:
        """
        更新文档内容。
        
        Args:
            document_id: 文档 ID
            content: 更新内容
            mode: 更新模式（overwrite/append）
            comment: 更新备注
            
        Returns:
            dict: 包含更新状态、更新时间、版本号等信息
            
        Raises:
            将 DingTalkAPIError 转换为 MCP 工具错误
        """
        try:
            return self.client.update_document(
                document_id=document_id,
                content=content,
                mode=mode,
                comment=comment,
            )
        except DingTalkAPIError as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code or "DINGTALK_ERROR",
                "details": e.details,
            }
    
    async def list_docs_tool(
        self,
        space_id: Optional[str] = None,
        folder_id: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "update_time",
        sort_order: str = "desc",
    ) -> dict:
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
            dict: 包含文档列表和分页信息
            
        Raises:
            将 DingTalkAPIError 转换为 MCP 工具错误
        """
        try:
            return self.client.list_documents(
                space_id=space_id,
                folder_id=folder_id,
                keyword=keyword,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order,
            )
        except DingTalkAPIError as e:
            return {
                "success": False,
                "error": e.message,
                "code": e.code or "DINGTALK_ERROR",
                "details": e.details,
            }


# 工具函数包装器，用于 MCP 注册
def create_mcp_tools(client: DingTalkClient):
    """
    创建 MCP 工具实例。
    
    Args:
        client: 钉钉客户端实例
        
    Returns:
        MCPTools: MCP 工具实例
    """
    return MCPTools(client)