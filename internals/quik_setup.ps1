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
    $userOut = ($out | &python $pyParse --output) -join "`n"
    if (![String]::IsNullOrWhitespace($userOut)) {
        Write-Host $userOut
    }
    $dir = ($out | &python $pyParse --cd)
    if (![String]::IsNullOrWhitespace($dir)) {
        Set-Location -LiteralPath $dir
    }
    $LASTEXITCODE=$exitcode
}

function Register-QuikAlias {
    param(
        [String]$Name
    )

    $completionScript = {
        param($commandName, $wordToComplete, $cursorPosition)
        # The trailing space is important to let the autocomplete script know if we are
        # looking for the next word or the completion of the current word.
        if ($cursorPosition -gt $wordToComplete.Length) {
            $wordToComplete = "$wordToComplete "
        }
        [array]$completion = (&python $pyParse --complete="$wordToComplete" --alias="$Name")
        if ($LASTEXITCODE -eq 0) {
            $completion
        } else {
            Get-ChildItem ".\$wordToComplete*" -Directory |
                ForEach-Object { Resolve-Path -Relative "$_" }
        }
    }.GetNewClosure()
    # GetNewClosure is necessary to ensure that $Name preserves its value after going out of scope.
    # See [https://techstronghold.com/scripting/@rudolfvesely/how-to-copy-values-of-variables-into-powershell-script-block-and-keep-it-intact-remember-it/]

    Set-Alias -Name "$Name" -Value Invoke-Quik -Scope Global
    Register-ArgumentCompleter -Native -CommandName $Name -ScriptBlock $completionScript
}

Register-QuikAlias -Name quik
# To register other aliases, you may call
# Register-QuikAlias -Name alias
