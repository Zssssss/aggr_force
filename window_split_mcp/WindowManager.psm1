# Windows窗口管理PowerShell脚本
# 用于在WSL中通过PowerShell管理Windows原生窗口

Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    using System.Text;
    using System.Collections.Generic;
    
    public class WindowManager {
        [DllImport("user32.dll")]
        public static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);
        
        [DllImport("user32.dll")]
        public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
        
        [DllImport("user32.dll")]
        public static extern int GetWindowTextLength(IntPtr hWnd);
        
        [DllImport("user32.dll")]
        public static extern bool IsWindowVisible(IntPtr hWnd);
        
        [DllImport("user32.dll")]
        public static extern IntPtr GetForegroundWindow();
        
        [DllImport("user32.dll")]
        public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
        
        [DllImport("user32.dll")]
        public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
        
        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
        
        [DllImport("user32.dll")]
        public static extern int GetSystemMetrics(int nIndex);
        
        public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
        
        [StructLayout(LayoutKind.Sequential)]
        public struct RECT {
            public int Left;
            public int Top;
            public int Right;
            public int Bottom;
        }
        
        public const uint SWP_NOZORDER = 0x0004;
        public const uint SWP_SHOWWINDOW = 0x0040;
        public const int SW_MAXIMIZE = 3;
        public const int SW_RESTORE = 9;
    }
"@

function Get-AllWindows {
    $windows = New-Object System.Collections.ArrayList
    
    $callback = {
        param($hWnd, $lParam)
        
        if ([WindowManager]::IsWindowVisible($hWnd)) {
            $length = [WindowManager]::GetWindowTextLength($hWnd)
            if ($length -gt 0) {
                $sb = New-Object System.Text.StringBuilder($length + 1)
                [WindowManager]::GetWindowText($hWnd, $sb, $sb.Capacity) | Out-Null
                $title = $sb.ToString()
                
                $rect = New-Object WindowManager+RECT
                [WindowManager]::GetWindowRect($hWnd, [ref]$rect) | Out-Null
                
                $window = @{
                    Handle = $hWnd.ToInt64()
                    Title = $title
                    X = $rect.Left
                    Y = $rect.Top
                    Width = $rect.Right - $rect.Left
                    Height = $rect.Bottom - $rect.Top
                }
                
                $null = $windows.Add($window)
            }
        }
        
        return $true
    }
    
    [WindowManager]::EnumWindows($callback, [IntPtr]::Zero) | Out-Null
    
    return $windows
}

function Get-ActiveWindow {
    $hWnd = [WindowManager]::GetForegroundWindow()
    
    if ($hWnd -eq [IntPtr]::Zero) {
        return $null
    }
    
    $length = [WindowManager]::GetWindowTextLength($hWnd)
    if ($length -gt 0) {
        $sb = New-Object System.Text.StringBuilder($length + 1)
        [WindowManager]::GetWindowText($hWnd, $sb, $sb.Capacity) | Out-Null
        $title = $sb.ToString()
        
        $rect = New-Object WindowManager+RECT
        [WindowManager]::GetWindowRect($hWnd, [ref]$rect) | Out-Null
        
        return @{
            Handle = $hWnd.ToInt64()
            Title = $title
            X = $rect.Left
            Y = $rect.Top
            Width = $rect.Right - $rect.Left
            Height = $rect.Bottom - $rect.Top
        }
    }
    
    return $null
}

function Move-WindowToPosition {
    param(
        [Parameter(Mandatory=$true)]
        [long]$Handle,
        [Parameter(Mandatory=$true)]
        [int]$X,
        [Parameter(Mandatory=$true)]
        [int]$Y,
        [Parameter(Mandatory=$true)]
        [int]$Width,
        [Parameter(Mandatory=$true)]
        [int]$Height
    )
    
    $hWnd = [IntPtr]::new($Handle)
    
    # 先恢复窗口（如果是最大化状态）
    [WindowManager]::ShowWindow($hWnd, [WindowManager]::SW_RESTORE) | Out-Null
    Start-Sleep -Milliseconds 100
    
    # 移动和调整大小
    $result = [WindowManager]::SetWindowPos(
        $hWnd,
        [IntPtr]::Zero,
        $X, $Y, $Width, $Height,
        [WindowManager]::SWP_NOZORDER -bor [WindowManager]::SWP_SHOWWINDOW
    )
    
    return $result
}

function Maximize-WindowByHandle {
    param(
        [Parameter(Mandatory=$true)]
        [long]$Handle
    )
    
    $hWnd = [IntPtr]::new($Handle)
    $result = [WindowManager]::ShowWindow($hWnd, [WindowManager]::SW_MAXIMIZE)
    return $result
}

function Get-ScreenSize {
    $width = [WindowManager]::GetSystemMetrics(0)  # SM_CXSCREEN
    $height = [WindowManager]::GetSystemMetrics(1) # SM_CYSCREEN
    
    return @{
        Width = $width
        Height = $height
    }
}

# 导出函数
Export-ModuleMember -Function Get-AllWindows, Get-ActiveWindow, Move-WindowToPosition, Maximize-WindowByHandle, Get-ScreenSize
