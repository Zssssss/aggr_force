# 快速获取DPI信息的PowerShell脚本
# 输出格式: dpiX,dpiY

try {
    Add-Type @'
using System;
using System.Runtime.InteropServices;
public class DpiHelper {
    [DllImport("user32.dll")]
    public static extern IntPtr GetDC(IntPtr hwnd);
    [DllImport("gdi32.dll")]
    public static extern int GetDeviceCaps(IntPtr hdc, int nIndex);
    [DllImport("user32.dll")]
    public static extern int ReleaseDC(IntPtr hwnd, IntPtr hdc);
    
    public static int GetDpiX() {
        IntPtr hdc = GetDC(IntPtr.Zero);
        int dpi = GetDeviceCaps(hdc, 88);
        ReleaseDC(IntPtr.Zero, hdc);
        return dpi;
    }
    
    public static int GetDpiY() {
        IntPtr hdc = GetDC(IntPtr.Zero);
        int dpi = GetDeviceCaps(hdc, 90);
        ReleaseDC(IntPtr.Zero, hdc);
        return dpi;
    }
}
'@

    $dpiX = [DpiHelper]::GetDpiX()
    $dpiY = [DpiHelper]::GetDpiY()
    
    # 输出简单格式，便于Python解析
    Write-Output "$dpiX,$dpiY"
} catch {
    # 出错时返回默认值96,96
    Write-Output "96,96"
}
