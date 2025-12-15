# client.py
import asyncio
import os
import sys
from dotenv import load_dotenv

# 导入 MCP 客户端相关模块
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 导入 Anthropic SDK
from anthropic import Anthropic

load_dotenv()  # 加载 .env 中的 API Key

# 1. 配置 Server 的启动参数
# 我们告诉 Client 去运行当前的 python 环境下的 server.py
server_params = StdioServerParameters(
    command=sys.executable, # 使用当前的 python 解释器
    args=["server.py"],     # 运行同目录下的 server.py
    env=None                # 继承当前环境变量
)

async def run_process():
    # 初始化 Anthropic 客户端
    anthropic = Anthropic()

    # 2. 建立与 MCP Server 的连接
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            # 3. 初始化协议并获取工具列表
            await session.initialize()
            
            # 获取 Server 提供的工具 (ListToolsResult)
            tools_result = await session.list_tools()
            
            # 将 MCP 的工具格式转换为 Claude API 需要的格式
            claude_tools = [{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in tools_result.tools]

            print(f"\n🔗 已连接到 MCP Server，发现工具: {[t.name for t in tools_result.tools]}")

            # 4. 模拟用户提问
            # 假设我们在 WSL 当前目录下有个 test.txt (稍后创建)
            user_query = "请读取当前目录下的 'test.txt' 文件，并告诉我里面写了什么。"
            print(f"\n👤 用户提问: {user_query}")

            # 5. 第一轮对话：发送 Prompt + Tools 给 Claude
            response = anthropic.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=1000,
                messages=[{"role": "user", "content": user_query}],
                tools=claude_tools
            )

            # 6. 处理 Claude 的回复
            # 检查 Claude 是否想要调用工具
            final_content = []
            
            if response.stop_reason == "tool_use":
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_args = content_block.input
                        print(f"\n🤖 Claude 想要调用工具: {tool_name} 参数: {tool_args}")

                        # 7. 真正执行工具调用 (通过 MCP 协议发送给 server.py)
                        result = await session.call_tool(tool_name, tool_args)
                        
                        # 提取工具执行结果
                        tool_output = result.content[0].text
                        print(f"📦 工具返回结果: {tool_output}")

                        # 8. 将工具结果回传给 Claude 进行最终总结
                        #我们需要构建包含上下文的消息历史
                        messages = [
                            {"role": "user", "content": user_query},
                            {"role": "assistant", "content": response.content},
                            {
                                "role": "user", 
                                "content": [
                                    {
                                        "type": "tool_result",
                                        "tool_use_id": content_block.id,
                                        "content": tool_output
                                    }
                                ]
                            }
                        ]

                        final_response = anthropic.messages.create(
                            model="claude-3-5-sonnet-latest",
                            max_tokens=1000,
                            messages=messages,
                            tools=claude_tools
                        )
                        print(f"\n🤖 Claude 最终回答:\n{final_response.content[0].text}")

            else:
                print(f"\n🤖 Claude 没有调用工具，直接回答: {response.content[0].text}")

if __name__ == "__main__":
    asyncio.run(run_process())