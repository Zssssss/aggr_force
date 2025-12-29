#!/usr/bin/env python3
"""
简单测试：测试移动窗口功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitor_tools import MonitorManager

def main():
    print("=" * 60)
    print("测试移动窗口功能")
    print("=" * 60)
    
    manager = MonitorManager()
    
    # 1. 列出显示器
    print("\n1. 显示器信息:")
    monitors = manager.get_monitors_info()
    for m in monitors:
        print(f"  显示器{m['MonitorNumber']}: {m['Width']}x{m['Height']} at ({m['Left']}, {m['Top']})")
    
    # 2. 查找Chrome窗口
    print("\n2. 查找Chrome窗口:")
    window = manager.get_window_by_title("Chrome")
    if window:
        print(f"  找到: {window['Title']}")
        
        # 3. 移动到显示器2
        print("\n3. 将Chrome移动到显示器2...")
        result = manager.move_window_by_title_to_monitor("Chrome", 2, maximize=False)
        
        if result['success']:
            print(f"  ✓ 成功移动到显示器{result['monitor_number']}")
            print(f"  窗口: {result['window_title']}")
            
            # 等待3秒
            import time
            print("\n  等待3秒后移回显示器1...")
            time.sleep(3)
            
            # 4. 移回显示器1
            result2 = manager.move_window_by_title_to_monitor("Chrome", 1, maximize=False)
            if result2['success']:
                print(f"  ✓ 成功移回显示器1")
            else:
                print(f"  ✗ 移回失败: {result2.get('error')}")
        else:
            print(f"  ✗ 移动失败: {result.get('error')}")
    else:
        print("  未找到Chrome窗口")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
