# PowerShell script to test deployed API
Write-Host "🧪 Testing Deployed API" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green

# Test health check first
Write-Host "`n🩺 Testing Health Check..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "https://llm-analysis-quiz-20q6.onrender.com/api/v1/quiz/health" -Method GET
    Write-Host "✅ Health Check Success!" -ForegroundColor Green
    Write-Host "Response: $($healthResponse | ConvertTo-Json)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test main quiz endpoint
Write-Host "`n🎯 Testing Quiz Solve Endpoint..." -ForegroundColor Yellow

$body = @{
    email = "24ds2000137@ds.study.iitm.ac.in"
    secret = "my-secret-123"
    url = "https://tds-llm-analysis.s-anand.net/demo"
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
}

try {
    $quizResponse = Invoke-RestMethod -Uri "https://llm-analysis-quiz-20q6.onrender.com/api/v1/quiz/solve" -Method POST -Body $body -Headers $headers
    Write-Host "✅ Quiz Endpoint Success!" -ForegroundColor Green
    Write-Host "Response: $($quizResponse | ConvertTo-Json -Depth 3)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Quiz Endpoint Failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host "Error Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

# Test Swagger UI
Write-Host "`n📚 Testing Swagger UI..." -ForegroundColor Yellow
try {
    $swaggerResponse = Invoke-WebRequest -Uri "https://llm-analysis-quiz-20q6.onrender.com/docs/" -Method GET
    if ($swaggerResponse.StatusCode -eq 200) {
        Write-Host "✅ Swagger UI accessible!" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Swagger UI Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 Testing Complete!" -ForegroundColor Green
Write-Host "🌐 Your deployed app: https://llm-analysis-quiz-20q6.onrender.com" -ForegroundColor Cyan
Write-Host "📚 Swagger UI: https://llm-analysis-quiz-20q6.onrender.com/docs/" -ForegroundColor Cyan
