#!/usr/bin/env python3
"""
测试 MCP 服务器的 stdio 模式
模拟真实的 MCP 客户端通信
"""
import subprocess
import json
import sys
from pathlib import Path

def test_stdio_communication():
    """测试 stdio 通信"""
    print("=" * 60)
    print("测试 MCP stdio 通信模式")
    print("=" * 60)
    
    server_path = Path(__file__).parent / "smart_mouse_move_mcp_server.py"
    
    try:
        # 启动服务器进程
        print("\n1. 启动 MCP 服务器...")
        process = subprocess.Popen(
            ["python3", str(server_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        print("✓ 服务器进程已启动 (PID: {})".format(process.pid))
        
        # 发送初始化请求
        print("\n2. 发送初始化请求...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # 读取响应（设置超时）
        import select
        import time
        
        timeout = 5
        start_time = time.time()
        response_lines = []
        
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                print("✗ 服务器进程意外退出")
                stderr_output = process.stderr.read()
                if stderr_output:
                    print(f"错误输出:\n{stderr_output}")
                return False
            
            # 尝试读取一行
            try:
                line = process.stdout.readline()
                if line:
                    response_lines.append(line.strip())
                    # 尝试解析为JSON
                    try:
                        response = json.loads(line)
                        print("✓ 收到初始化响应")
                        print(f"  响应ID: {response.get('id')}")
                        if 'result' in response:
                            print(f"  服务器信息: {response['result'].get('serverInfo', {})}")
                        break
                    except json.JSONDecodeError:
                        # 不是有效的JSON，可能是日志输出
                        print(f"  [非JSON输出] {line.strip()}")
            except Exception as e:
                print(f"读取响应时出错: {e}")
                break
        else:
            print("✗ 等待响应超时")
            print(f"已读取的行: {response_lines}")
            return False
        
        # 终止进程
        print("\n3. 终止服务器...")
        process.terminate()
        try:
            process.wait(timeout=2)
            print("✓ 服务器已正常终止")
        except subprocess.TimeoutExpired:
            process.kill()
            print("⚠ 服务器被强制终止")
        
        print("\n" + "=" * 60)
        print("stdio 通信测试完成")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        if 'process' in locals():
            process.kill()
        
        return False

if __name__ == "__main__":
    success = test_stdio_communication()
    sys.exit(0 if success else 1)
