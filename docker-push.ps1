# Script tự động tag và push Docker image lên Docker Hub
# Usage: .\docker-push.ps1 -Username YOUR_USERNAME [-Tag latest] [-ImageName videomae-service]

param(
    [Parameter(Mandatory=$true)]
    [string]$Username,
    
    [Parameter(Mandatory=$false)]
    [string]$Tag = "latest",
    
    [Parameter(Mandatory=$false)]
    [string]$ImageName = "videomae-service"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker Hub Push Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra Docker có chạy không
Write-Host "[1/5] Kiểm tra Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker không khả dụng"
    }
    Write-Host "✓ Docker đã sẵn sàng: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Lỗi: Docker chưa được cài đặt hoặc chưa chạy" -ForegroundColor Red
    Write-Host "   Vui lòng cài Docker Desktop và đảm bảo nó đang chạy" -ForegroundColor Red
    exit 1
}

# Kiểm tra image có tồn tại không
Write-Host ""
Write-Host "[2/5] Kiểm tra image local..." -ForegroundColor Yellow
$imageExists = docker images -q "$ImageName" 2>&1
if (-not $imageExists) {
    Write-Host "❌ Image '$ImageName' không tồn tại" -ForegroundColor Red
    Write-Host "   Vui lòng build image trước: docker build -t $ImageName ." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Image '$ImageName' đã tồn tại" -ForegroundColor Green

# Kiểm tra đăng nhập Docker Hub
Write-Host ""
Write-Host "[3/5] Kiểm tra đăng nhập Docker Hub..." -ForegroundColor Yellow
try {
    $loginCheck = docker info 2>&1 | Select-String "Username"
    if (-not $loginCheck) {
        Write-Host "⚠ Chưa đăng nhập Docker Hub" -ForegroundColor Yellow
        Write-Host "   Đang yêu cầu đăng nhập..." -ForegroundColor Yellow
        docker login
        if ($LASTEXITCODE -ne 0) {
            throw "Đăng nhập thất bại"
        }
    } else {
        Write-Host "✓ Đã đăng nhập Docker Hub" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Lỗi đăng nhập: $_" -ForegroundColor Red
    Write-Host "   Vui lòng chạy: docker login" -ForegroundColor Red
    exit 1
}

# Tag image
$remoteImage = "$Username/$ImageName`:$Tag"
Write-Host ""
Write-Host "[4/5] Tag image..." -ForegroundColor Yellow
Write-Host "   Local:  $ImageName" -ForegroundColor Gray
Write-Host "   Remote: $remoteImage" -ForegroundColor Gray

docker tag "$ImageName" "$remoteImage"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Lỗi khi tag image" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Đã tag image thành công" -ForegroundColor Green

# Push image
Write-Host ""
Write-Host "[5/5] Push image lên Docker Hub..." -ForegroundColor Yellow
Write-Host "   Đang push: $remoteImage" -ForegroundColor Gray
Write-Host "   (Quá trình này có thể mất vài phút...)" -ForegroundColor Gray
Write-Host ""

docker push "$remoteImage"
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Lỗi khi push image" -ForegroundColor Red
    Write-Host ""
    Write-Host "Các nguyên nhân có thể:" -ForegroundColor Yellow
    Write-Host "  1. Username không đúng: $Username" -ForegroundColor Yellow
    Write-Host "  2. Chưa đăng nhập: docker login" -ForegroundColor Yellow
    Write-Host "  3. Repository name không hợp lệ" -ForegroundColor Yellow
    Write-Host "  4. Không có quyền truy cập" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Hoàn thành!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Image đã được push lên Docker Hub:" -ForegroundColor Green
Write-Host "  $remoteImage" -ForegroundColor Cyan
Write-Host ""
Write-Host "Người khác có thể pull và sử dụng:" -ForegroundColor Yellow
Write-Host "  docker pull $remoteImage" -ForegroundColor Gray
Write-Host ""
Write-Host "Chạy container:" -ForegroundColor Yellow
Write-Host "  docker run -d -p 8000:8000 \`" -ForegroundColor Gray
Write-Host "    -v /path/to/videomae_finetuned_final:/models/videomae_finetuned_final \`" -ForegroundColor Gray
Write-Host "    $remoteImage" -ForegroundColor Gray
Write-Host ""

