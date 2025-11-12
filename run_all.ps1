param(
    [int] $Repeat = 1
)

$root = Get-Location
# ensure venv exists and is set up
if (-not (Test-Path "$root\.venv\Scripts\Activate.ps1")) {
    Write-Output "Virtual env not found — running setup.ps1 to prepare environment..."
    & "$root\setup.ps1"
}

# Activate venv for current session
. "$root\.venv\Scripts\Activate.ps1"

try {
    Push-Location "$root\Project_A_PreMitigation_SQLi"
    Write-Output "Running tests for Project A (pre-mitigation)..."
    # forward repeat argument to run_tests wrapper
    & .\run_tests.ps1 --repeat $Repeat
    Pop-Location

    Push-Location "$root\Project_B_PostMitigation_SQLi"
    Write-Output "Running tests for Project B (post-mitigation)..."
    & .\run_tests.ps1 --repeat $Repeat
    Pop-Location
}
catch {
    Write-Error "Error running tests: $_"
}

# generate compare report using PowerShell JSON handling
$prePath = Join-Path $root "Project_A_PreMitigation_SQLi\results\results_pre.json"
$postPath = Join-Path $root "Project_B_PostMitigation_SQLi\results\results_post.json"

$pre = @{}
$post = @{}
if (Test-Path $prePath) {
    $preJson = Get-Content -Raw -Path $prePath | ConvertFrom-Json
    $pre = $preJson
}
if (Test-Path $postPath) {
    $postJson = Get-Content -Raw -Path $postPath | ConvertFrom-Json
    $post = $postJson
}

$pa = $pre.metrics
$pb = $post.metrics

$pre_success = 0.0
$pre_latency = 0.0
$pre_leaks = 0
$post_success = 0.0
$post_latency = 0.0
$post_leaks = 0
if ($pa) {
    $pre_success = [double]($pa.attack_success_rate)
    $pre_latency = [double]($pa.avg_latency)
    $pre_leaks = [int]($pa.leaks)
}
if ($pb) {
    $post_success = [double]($pb.attack_success_rate)
    $post_latency = [double]($pb.avg_latency)
    $post_leaks = [int]($pb.leaks)
}

$score_pre = [Math]::Max(0, 100 - $pre_success)
$latency_penalty = 0.0
if ($pre_latency -gt 0) {
    $latency_penalty = [Math]::Max(0.0, (($post_latency - $pre_latency)/$pre_latency) * 100.0)
}
$score_post = [Math]::Max(0, $score_pre - $latency_penalty)

$report = @"
# Comparison Report

|Metric|Pre-Mitigation|Post-Mitigation|Delta|
|---|---:|---:|---:|
|Attack success %|{0:N2}|{1:N2}|{2:N2}|
|Average Latency (s)|{3:N3}|{4:N3}|{5:N3}|
|Leaks (count)|{6}|{7}|{8}|

**Security score (0-100)**
- Pre: {9:N1}
- Post: {10:N1}
"@ -f $pre_success, $post_success, ($pre_success - $post_success), $pre_latency, $post_latency, ($post_latency - $pre_latency), $pre_leaks, $post_leaks, ($pre_leaks - $post_leaks), $score_pre, $score_post

Set-Content -Path (Join-Path $root 'compare_report.md') -Value $report -Encoding UTF8
Write-Output $report
