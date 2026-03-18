<#
.SYNOPSIS
  로컬 환경 설정 — 클론 후 junction/하드링크 복원 (1회 실행)

.EXAMPLE
  .\setup.ps1
#>
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$SharedDir = Join-Path $RepoRoot "shared"
$SharedScripts = Join-Path $SharedDir "scripts"
$SharedEnv = Join-Path $SharedDir ".env"
$SharedEnvExample = Join-Path $SharedDir ".env.example"

$ScriptSkills = @("git-mr-review", "google-forms-viewer", "jira-filter-summarizer", "wiki-page-summarizer")

function New-JunctionSafe($Path, $Target) {
    if (Test-Path $Path) {
        $item = Get-Item $Path -Force
        if ($item.LinkType -eq "Junction") {
            Write-Host "  [skip] junction: $Path" -ForegroundColor DarkGray
            return
        }
        Remove-Item $Path -Recurse -Force
    }
    New-Item -ItemType Junction -Path $Path -Target $Target | Out-Null
    Write-Host "  [ok] junction: $Path" -ForegroundColor Green
}

function New-HardLinkSafe($Path, $Target) {
    if (Test-Path $Path) {
        Write-Host "  [skip] $Path" -ForegroundColor DarkGray
        return
    }
    New-Item -ItemType HardLink -Path $Path -Target $Target | Out-Null
    Write-Host "  [ok] hardlink: $Path" -ForegroundColor Green
}

Write-Host "`n=== 로컬 설정 (junction/하드링크 복원) ===" -ForegroundColor Cyan

foreach ($platform in @(".claude", ".cursor")) {
    $platformDir = Join-Path $RepoRoot $platform
    Write-Host "`n[$platform]" -ForegroundColor Yellow

    if (Test-Path $SharedEnv) {
        New-HardLinkSafe (Join-Path $platformDir ".env") $SharedEnv
    }
    New-HardLinkSafe (Join-Path $platformDir ".env.example") $SharedEnvExample

    foreach ($skill in $ScriptSkills) {
        $skillDir = Join-Path $platformDir "skills\$skill"
        if (Test-Path $skillDir) {
            New-JunctionSafe (Join-Path $skillDir "scripts") (Join-Path $SharedScripts $skill)
        }
    }
}

Write-Host "`n완료." -ForegroundColor Cyan
