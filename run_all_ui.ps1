Set-StrictMode -Version Latest
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $root
Write-Host "Running Pre-Mitigation tests..."
& "$root\Project_A_PreMitigation_UI\run_ui_tests.ps1"
Write-Host "Running Post-Mitigation tests..."
& "$root\Project_B_PostMitigation_UI\run_ui_tests.ps1"

$pre = Join-Path $root 'Project_A_PreMitigation_UI\results_pre.json'
$post = Join-Path $root 'Project_B_PostMitigation_UI\results_post.json'
if (-not (Test-Path $pre) -or -not (Test-Path $post)) {
    Write-Host 'Missing results files. Run both tests to generate results_pre.json and results_post.json'
    Exit 1
}

$pre_r = Get-Content $pre | ConvertFrom-Json
$post_r = Get-Content $post | ConvertFrom-Json

$changes = [ordered]@{
    xss_success_pct_drop = $pre_r.summary.xss_success_pct - $post_r.summary.xss_success_pct
    secrets_exposed_pct_drop = $pre_r.summary.secrets_exposed_pct - $post_r.summary.secrets_exposed_pct
    security_score_gain = $post_r.summary.security_score - $pre_r.summary.security_score
}

$md = @()
$md += '# UI Security Comparison Report'
$md += '`
## Metrics (Pre vs Post)`'
$md += '| Metric | Pre | Post | Delta |'
$md += '|---|---:|---:|---:|'
$md += "| XSS success % | {0:N2} | {1:N2} | {2:N2} |" -f $pre_r.summary.xss_success_pct, $post_r.summary.xss_success_pct, $changes.xss_success_pct_drop
$md += "| Secrets exposure % | {0:N2} | {1:N2} | {2:N2} |" -f $pre_r.summary.secrets_exposed_pct, $post_r.summary.secrets_exposed_pct, $changes.secrets_exposed_pct_drop
$md += "| Security score | {0} | {1} | {2:+} |" -f $pre_r.summary.security_score, $post_r.summary.security_score, $changes.security_score_gain
$md += '`
## Summary`'
$md += 'Security improvements were measured across the provided test payloads and environments. The patched UI aims to reduce XSS and secrets exposure via input sanitization, CSP, and safe DOM updates.'

$reportFile = Join-Path $root 'compare_ui_security_report.md'
$md -join "`n" | Out-File -FilePath $reportFile -Encoding utf8
Write-Host "Comparison report written to $reportFile"

Pop-Location
