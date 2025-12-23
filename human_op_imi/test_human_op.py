"""
测试人类操作模拟 MCP 模块
"""

import asyncio
from human_op_imi import HumanOpTools


async def test_mouse_move():
    """测试鼠标移动功能"""
    tools = HumanOpTools()
    
    # 初始状态
    initial_state = await tools.get_simulation_state_tool()
    print(f"初始状态: {initial_state}")
    
    # 测试鼠标移动
    result = await tools.mouse_move_tool(x=100, y=200, duration=0.5)
    print(f"鼠标移动结果: {result}")
    
    # 检查是否存在问题
    if result["from"] == result["to"]:
        print("\n❌ 发现问题：'from' 和 'to' 坐标相同！")
        print(f"   应该是从初始位置 {initial_state['state']['mouse_position']} 移动到 (100, 200)")


async def test_all_tools():
    """测试所有工具"""
    tools = HumanOpTools()
    
    # 测试鼠标点击
    print("\n1. 测试鼠标点击：")
    click_result = await tools.mouse_click_tool(x=500, y=300, button="left", double_click=False)
    print(f"   结果: {click_result}")
    
    # 测试键盘输入
    print("\n2. 测试键盘输入：")
    type_result = await tools.keyboard_type_tool(text="Hello World", speed=0.1)
    print(f"   结果: {type_result}")
    
    # 测试剪贴板复制
    print("\n3. 测试剪贴板复制：")
    copy_result = await tools.clipboard_copy_tool(content="Test clipboard content")
    print(f"   结果: {copy_result}")
    
    # 测试剪贴板粘贴
    print("\n4. 测试剪贴板粘贴：")
    paste_result = await tools.clipboard_paste_tool()
    print(f"   结果: {paste_result}")


if __name__ == "__main__":
    asyncio.run(test_mouse_move())
    asyncio.run(test_all_tools())