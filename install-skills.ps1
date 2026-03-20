<#
.SYNOPSIS
  스킬 설치 — 전역 또는 특정 프로젝트에 스킬을 설치

.EXAMPLE
  .\install-skills.ps1 -Target global                                         # .claude 전체 스킬을 전역에 설치
  .\install-skills.ps1 -Target global -Platform cursor                        # .cursor 전체 스킬을 전역에 설치
  .\install-skills.ps1 -Target global -Skills git-mr-review                   # 특정 스킬만 전역 설치
  .\install-skills.ps1 -Target global -Skills git-mr-review -Force            # 이미 설치된 스킬을 강제 재설치
  .\install-skills.ps1 -Target D:\Projects\myapp                              # 특정 프로젝트에 설치
  .\install-skills.ps1 -Target D:\Projects\myapp -Platform cursor -Skills git-mr-review,wiki-page-summarizer
#>
param(
    [string]$Target,
    [ValidateSet("claude", "cursor")]
    [string]$Platform = "claude",
    [string[]]$Skills,
    [switch]$Force
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

if (-not $Target) {
    Write-Host @"

  스킬 설치 - 전역 또는 특정 프로젝트에 스킬을 설치합니다.

  사용법:
    .\install-skills.ps1 -Target <global|경로> [-Platform <claude|cursor>] [-Skills <스킬,...>] [-Force]

  파라미터:
    -Target     설치 대상. "global" (전역) 또는 프로젝트 경로 (필수)
    -Platform   소스 플랫폼. claude(기본) 또는 cursor
    -Skills     설치할 스킬 이름. 생략 시 전체 스킬 설치
    -Force      이미 설치된 스킬을 삭제 후 재설치

  예시:
    .\install-skills.ps1 -Target global                              # .claude 전체 스킬을 전역에 설치
    .\install-skills.ps1 -Target global -Platform cursor             # .cursor 전체 스킬을 전역에 설치
    .\install-skills.ps1 -Target global -Skills git-mr-review        # 특정 스킬만 전역 설치
    .\install-skills.ps1 -Target global -Skills git-mr-review -Force # 강제 재설치
    .\install-skills.ps1 -Target D:\Projects\myapp                   # 특정 프로젝트에 설치
    .\install-skills.ps1 -Target D:\Projects\myapp -Platform cursor -Skills git-mr-review,wiki-page-summarizer

"@
    return
}
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$SharedDir = Join-Path $RepoRoot "shared"
$SharedScripts = Join-Path $SharedDir "scripts"
$SharedEnv = Join-Path $SharedDir ".env"

# 스킬 → 공유 스크립트 매핑
# 단순 매핑: skill/scripts/ → shared/scripts/<skill>/
$SimpleScriptSkills = @("git-mr-review", "google-forms-viewer")
# 서비스별 매핑: skill/scripts/<service>/ → shared/scripts/<service>/
$ServiceScriptSkills = @{
    "jira-filter-summarizer" = @("jira")
    "jira-bug-analyzer"      = @("jira")
    "wiki-page-summarizer"   = @("jira", "confluence")
}

$PlatformSkillsDir = Join-Path $RepoRoot ".$Platform\skills"
$AllSkills = Get-ChildItem $PlatformSkillsDir -Directory | Select-Object -ExpandProperty Name

if (-not $Skills -or $Skills.Count -eq 0) {
    $Skills = $AllSkills
}

foreach ($s in $Skills) {
    if ($s -notin $AllSkills) {
        Write-Error "알 수 없는 스킬: $s  사용 가능: $($AllSkills -join ', ')"
        return
    }
}

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

function New-LinkOrCopy($Path, $Target) {
    if (Test-Path $Path) {
        Write-Host "  [skip] $Path" -ForegroundColor DarkGray
        return
    }
    $dir = Split-Path -Parent $Path
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    try {
        New-Item -ItemType HardLink -Path $Path -Target $Target | Out-Null
        Write-Host "  [ok] hardlink: $Path" -ForegroundColor Green
    } catch {
        Copy-Item $Target $Path -Force
        Write-Host "  [ok] copy: $Path" -ForegroundColor Yellow
    }
}

function Copy-Safe($Path, $Source) {
    $dir = Split-Path -Parent $Path
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Copy-Item $Source $Path -Force
    Write-Host "  [ok] copy: $Path" -ForegroundColor Green
}

# 설치 대상 디렉토리
if ($Target -eq "global") {
    $TargetPlatformDir = Join-Path $env:USERPROFILE ".$Platform"
} else {
    $TargetPlatformDir = Join-Path $Target ".$Platform"
}
$TargetSkillsDir = Join-Path $TargetPlatformDir "skills"

Write-Host "`n=== 스킬 설치: $TargetPlatformDir ===" -ForegroundColor Cyan
Write-Host "플랫폼: $Platform | 스킬: $($Skills -join ', ')`n" -ForegroundColor Yellow

# .env
if (Test-Path $SharedEnv) {
    New-LinkOrCopy (Join-Path $TargetPlatformDir ".env") $SharedEnv
} else {
    Write-Host "  [warn] shared/.env가 없습니다. shared/.env.example을 복사해 설정하세요." -ForegroundColor DarkYellow
}

# 스킬
$installedCount = 0
$skippedCount = 0

foreach ($skill in $Skills) {
    $srcSkillDir = Join-Path $PlatformSkillsDir $skill
    $dstSkillDir = Join-Path $TargetSkillsDir $skill
    $dstSkillMd = Join-Path $dstSkillDir "SKILL.md"

    # 이미 설치 여부 확인
    if ((Test-Path $dstSkillMd) -and -not $Force) {
        Write-Host "  [skip] $skill — 이미 설치됨 (재설치: -Force 옵션 사용)" -ForegroundColor DarkGray
        $skippedCount++
        continue
    }

    Write-Host "`n[$skill]" -ForegroundColor Yellow

    # -Force: 기존 scripts 디렉토리 삭제 후 재설치
    if ($Force) {
        $dstScripts = Join-Path $dstSkillDir "scripts"
        if (Test-Path $dstScripts) {
            Remove-Item $dstScripts -Recurse -Force
            Write-Host "  [clean] scripts 삭제" -ForegroundColor DarkYellow
        }
    }

    $skillMd = Join-Path $srcSkillDir "SKILL.md"
    if (Test-Path $skillMd) {
        Copy-Safe $dstSkillMd $skillMd
    }

    if ($skill -in $SimpleScriptSkills) {
        New-JunctionSafe (Join-Path $dstSkillDir "scripts") (Join-Path $SharedScripts $skill)
    } elseif ($ServiceScriptSkills.ContainsKey($skill)) {
        $scriptsDir = Join-Path $dstSkillDir "scripts"
        if (-not (Test-Path $scriptsDir)) { New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null }
        foreach ($svc in $ServiceScriptSkills[$skill]) {
            New-JunctionSafe (Join-Path $scriptsDir $svc) (Join-Path $SharedScripts $svc)
        }
    }

    $installedCount++
}

# 결과 요약
if ($skippedCount -gt 0 -and $installedCount -eq 0) {
    Write-Host "`n모든 스킬이 이미 설치되어 있습니다. 재설치하려면 -Force 옵션을 사용하세요." -ForegroundColor DarkYellow
} else {
    Write-Host "`n완료. (설치: $installedCount, 건너뜀: $skippedCount)" -ForegroundColor Cyan
}
