# PowerShell wrapper to run the bash orchestration
$script = Join-Path $PSScriptRoot 'run_all.sh'
if (Test-Path $script) {
    $bashCmd = Get-Command bash -ErrorAction SilentlyContinue
    if ($bashCmd) {
        # Convert Windows path to POSIX-like path for bash/WSL/Git Bash
        $posixPwd = $PSScriptRoot -replace '\\','/'
        if ($posixPwd -match '([A-Za-z]):(.*)') {
            $drive = $matches[1].ToLower()
            $rest = $matches[2]
            if ($rest.StartsWith('/')) { $rest = $rest.Substring(1) }
            # Git Bash path variant
            $posix_gitbash = "/$drive/$rest"
            # WSL path variant
            $posix_wsl = "/mnt/$drive/$rest"
        } else {
            $posix_gitbash = $posixPwd
            $posix_wsl = $posixPwd
        }
        # Choose a path that exists in the selected bash
        $checkGit = bash -lc "if [ -d '$posix_gitbash' ]; then echo YES; else echo NO; fi" 2>&1 | Select-String YES
        if ($checkGit) {
            $posix = $posix_gitbash
        } else {
            $checkWsl = bash -lc "if [ -d '$posix_wsl' ]; then echo YES; else echo NO; fi" 2>&1 | Select-String YES
            if ($checkWsl) {
                $posix = $posix_wsl
            } else {
                Write-Host "Unable to find the repo path in bash. Please run './run_all.sh' inside Git Bash or WSL in the repository folder";
                return
            }
        }
        Write-Host "Starting bash in: $posix"
        $cmd = "cd '$posix' ; ./run_all.sh"
        bash -lc $cmd
    } else {
        Write-Host "Bash is not available. Please run run_all.sh using Git Bash or WSL, or use PowerShell directly to run setup and run scripts."
    }
} else {
    Write-Host "run_all.sh not found."
}