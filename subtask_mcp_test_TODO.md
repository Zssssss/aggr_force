完整工作流程
1. 调用 screenshot MCP 截取屏幕
   ↓
2. 调用 screenshot MCP 读取图片
   ↓
3. AI助手分析图片，识别当前鼠标位置和目标文本位置
   ↓
4. 调用 mouse-move MCP 移动鼠标到目标位置
   ↓
5. 调用 mouse-move MCP 验证是否到达
   ↓
6. 如未到达，重复步骤1-5