<#
.SYNOPSIS
    Developer task runner for awesome-antigravity-tools on Windows PowerShell.
.EXAMPLE
    pwsh .\scripts\dev.ps1 -Task all
    pwsh .\scripts\dev.ps1 -Task serve
#>
[CmdletBinding()]
param(
    [ValidateSet('all', 'validate', 'generate', 'export', 'build-site', 'test', 'mcp-test', 'audit', 'discover', 'doctor', 'serve')]
    [string]$Task = 'all',
    [int]$Port = 8765
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot

function Invoke-Step {
    param([Parameter(Mandatory)][scriptblock]$Command)
    & $Command
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

try {
    switch ($Task) {
        'validate' {
            Invoke-Step { python scripts/aat_cli.py verify --check-sync --strict-warnings }
        }
        'generate' {
            Invoke-Step { python scripts/aat_cli.py sync }
        }
        'export' {
            Invoke-Step { python scripts/export_catalog.py }
        }
        'build-site' {
            Invoke-Step { python scripts/build_site.py }
        }
        'test' {
            Invoke-Step { python -m unittest discover -s tests -v }
            Invoke-Step { node --check docs/catalog-logic.js }
            Invoke-Step { node --check docs/insights.js }
            Invoke-Step { node --check docs/app.js }
            Invoke-Step { node --test tests/test_web.mjs }
        }
        'mcp-test' {
            Invoke-Step { python scripts/mcp_server.py --self-test }
        }
        'audit' {
            Invoke-Step { python scripts/health-check.py --use-gh-cli }
            Invoke-Step { python scripts/aat_cli.py sync }
        }
        'discover' {
            Invoke-Step { python scripts/discover_candidates.py --use-gh-cli --limit 15 }
        }
        'doctor' {
            Invoke-Step { python scripts/aat_cli.py doctor }
        }
        'serve' {
            Write-Host "Serving docs/ at http://127.0.0.1:$Port/ (Ctrl+C to stop)" -ForegroundColor Cyan
            Invoke-Step { python -m http.server $Port --directory docs }
        }
        'all' {
            Invoke-Step { python scripts/aat_cli.py sync }
            Invoke-Step { python scripts/aat_cli.py verify --check-sync --strict-warnings }
            Invoke-Step { python -m unittest discover -s tests -v }
            Invoke-Step { node --test tests/test_web.mjs }
            Invoke-Step { python scripts/mcp_server.py --self-test }
        }
    }
} finally {
    Pop-Location
}
