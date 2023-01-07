# This is a PowerShell port of the quik_setup.sh file.
# Its structure is closer to the bash file than to the command prompt file,
# in terms of the approach taken.

# Get this file's directory
# While $PSScriptRoot should be available, this should be more backwards compatible.
# See https://stackoverflow.com/a/3667376 (Roman Kuzmin)
$scriptPath = Get-Item (Split-Path $MyInvocation.MyCommand.Path -Parent)

# Variables we'll use for invocation
$pyQuik = Get-Item -Path (Join-Path -Path $scriptPath.parent -ChildPath "quik.py")
$pyParse = Get-Item -Path (Join-Path -Path $scriptPath -ChildPath "output_parse.py")

# Set the QUIK_JSON environment variable
$env:QUIK_JSON = Convert-Path -Path (Join-Path -Path $scriptPath.parent -ChildPath "quik.json")

function Invoke-Quik {
    $out = (&python $pyQuik @args) -join "`n"
    $exitcode=$LASTEXITCODE
    if ($out | Select-String -Pattern '+cd' -SimpleMatch -Quiet) {
        Write-Host ($out | &python $pyParse --output)
        $dir = ($out | &python $pyParse --cd)
        Set-Location -LiteralPath $dir
    } else {
        Write-Host $out
    }
    $LASTEXITCODE=$exitcode
}

Set-Alias -Name quik -Value Invoke-Quik

Register-ArgumentCompleter -Native -CommandName quik -ScriptBlock {
    param($commandName, $wordToComplete, $cursorPosition)
    $completion = &python $pyParse --complete="$wordToComplete"
    if ($LASTEXITCODE -eq 0) {
        $completion
    } else {
        Get-ChildItem ".\$wordToComplete*" | ForEach-Object { Resolve-Path -Relative "$_" }
    }
}
