<#
.SYNOPSIS
    Developer task runner for awesome-antigravity-tools on Windows PowerShell.
.EXAMPLE
    pwsh .\scripts\dev.ps1 -Task all
    pwsh .\scripts\dev.ps1 -Task serve
#>
[CmdletBinding()]
param(
    [ValidateSet('all', 'validate', 'generate', 'export', 'build-site', 'test', 'audit', 'discover', 'doctor', 'serve')]
    [string]$Task = 'all',
    [int]$Port = 8765
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot

try {
    switch ($Task) {
        'validate' {
            python scripts/aat_cli.py verify --check-sync --strict-warnings
        }
        'generate' {
            python scripts/aat_cli.py sync
        }
        'export' {
            python scripts/export_catalog.py
        }
        'build-site' {
            python scripts/build_site.py
        }
        'test' {
            python -m unittest discover -s tests -v
            node --check docs/catalog-logic.js
            node --check docs/insights.js
            node --check docs/app.js
            node --test tests/test_web.mjs
        }
        'audit' {
            python scripts/health-check.py --use-gh-cli
            python scripts/aat_cli.py sync
        }
        'discover' {
            python scripts/discover_candidates.py --use-gh-cli --limit 15
        }
        'doctor' {
            python scripts/aat_cli.py doctor
        }
        'serve' {
            Write-Host "Serving docs/ at http://127.0.0.1:$Port/ (Ctrl+C to stop)" -ForegroundColor Cyan
            python -m http.server $Port --directory docs
        }
        'all' {
            python scripts/aat_cli.py sync
            python scripts/aat_cli.py verify --check-sync --strict-warnings
            python -m unittest discover -s tests -v
            node --test tests/test_web.mjs
        }
    }
} finally {
    Pop-Location
}
