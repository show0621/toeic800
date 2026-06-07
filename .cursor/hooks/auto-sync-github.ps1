# Cursor stop hook: auto commit + push when the agent finishes (if there are changes).
# Disable: create an empty file  .cursor/auto-sync.disabled
$ErrorActionPreference = "Continue"

$null = [Console]::In.ReadToEnd()

$logDir = Join-Path $PSScriptRoot "."
$logFile = Join-Path $logDir "auto-sync.log"

function Write-Log([string]$msg) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
    Add-Content -Path $logFile -Value $line -Encoding UTF8
}

try {
    $root = git rev-parse --show-toplevel 2>$null
    if (-not $root) { exit 0 }
    Set-Location $root

    $remote = (git remote get-url origin 2>$null) -join ""
    if ($remote -notmatch 'show0621/toeic800') {
        Write-Log "Skipped (remote is not show0621/toeic800): $remote"
        exit 0
    }

    $disableFile = Join-Path $root ".cursor/auto-sync.disabled"
    if (Test-Path $disableFile) {
        Write-Log "Skipped (auto-sync disabled)."
        exit 0
    }

    $porcelain = git status --porcelain 2>$null
    if (-not $porcelain) { exit 0 }

    $forbidden = @(
        ".env",
        ".streamlit/secrets.toml",
        "secrets.toml"
    )

    git add -A 2>$null

    foreach ($pat in $forbidden) {
        git reset HEAD -- $pat 2>$null | Out-Null
    }

    git reset HEAD -- "data/toeic800.db" 2>$null | Out-Null
    git reset HEAD -- "data/audio/*.mp3" 2>$null | Out-Null
    git reset HEAD -- ".cursor/hooks/auto-sync.log" 2>$null | Out-Null

    $staged = @(git diff --cached --name-only 2>$null)
    $safe = @()
    foreach ($file in $staged) {
        $block = $false
        foreach ($pat in $forbidden) {
            if ($file -eq $pat -or $file -like "*\$pat" -or $file -like "*/$pat") {
                $block = $true
                break
            }
        }
        if ($file -eq "data/toeic800.db" -or $file -like "data/audio/*") { $block = $true }
        if ($file -eq ".cursor/hooks/auto-sync.log") { $block = $true }
        if ($block) {
            git reset HEAD -- $file 2>$null | Out-Null
            Write-Log "Unstaged blocked file: $file"
        } else {
            $safe += $file
        }
    }

    if ($safe.Count -eq 0) {
        Write-Log "Nothing safe to commit after filtering."
        exit 0
    }

    $summary = ($safe | Select-Object -First 5) -join ", "
    if ($safe.Count -gt 5) { $summary += ", ..." }
    $msg = "Auto-sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm') — $summary"

    git commit -m $msg 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Commit skipped or failed (exit $LASTEXITCODE)."
        exit 0
    }

    $pushOut = git push origin HEAD 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Pushed: $summary"
    } else {
        Write-Log "Push failed: $pushOut"
    }
} catch {
    Write-Log "Error: $_"
}

exit 0
