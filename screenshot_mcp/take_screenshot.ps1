Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# 生成文件名
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$filename = "screenshot_$timestamp.png"
$filepath = Join-Path -Path $PSScriptRoot -ChildPath $filename

Write-Host "Attempting to take screenshot..."

try {
    # 获取主屏幕的边界
    $screen = [System.Windows.Forms.Screen]::PrimaryScreen
    $bounds = $screen.Bounds
    
    $width = $bounds.Width
    $height = $bounds.Height
    
    # 创建位图对象
    $bitmap = New-Object System.Drawing.Bitmap $width, $height
    
    # 创建图形对象
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    
    # 截图
    $graphics.CopyFromScreen($bounds.Left, $bounds.Top, 0, 0, $bitmap.Size)
    
    # 保存图片
    $bitmap.Save($filepath, [System.Drawing.Imaging.ImageFormat]::Png)
    
    Write-Host "Successfully saved screenshot to: $filepath"
    
    # 输出图片信息
    Write-Host "Image Information:"
    Write-Host "  Filename: $filename"
    Write-Host "  Size: $($bitmap.Width) x $($bitmap.Height) (Width x Height)"
    Write-Host "  Format: PNG"
    
    # 释放资源
    $graphics.Dispose()
    $bitmap.Dispose()
}
catch {
    Write-Host "Error taking screenshot: $_"
    exit 1
}
