import datetime
import os
import sys
from PIL import Image

def take_screenshot_and_info():
    # 生成文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    # 确保保存到当前脚本所在目录 (即 screen_op)
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    print(f"Attempting to take screenshot...")
    
    try:
        # 尝试使用 mss 进行截图
        import mss
        with mss.mss() as sct:
            sct.shot(output=filepath)
            
        print(f"Successfully saved screenshot to: {filepath}")

        # 获取图片信息
        with Image.open(filepath) as img:
            print("Image Information:")
            print(f"  Filename: {filename}")
            print(f"  Format: {img.format}")
            print(f"  Size: {img.size} (Width x Height)")
            print(f"  Mode: {img.mode}")
            
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        # 尝试提供更多调试信息
        if "DISPLAY" not in os.environ:
            print("Hint: DISPLAY environment variable is not set. GUI operations might fail in WSL without an X server.")
        sys.exit(1)

if __name__ == "__main__":
    take_screenshot_and_info()
