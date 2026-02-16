# NEURAL BET - PowerShell Launch Script
# Add the NEURAL_BET folder to your PATH to run 'neuralbet' from anywhere

$projectPath = "c:\Users\LEANDRE\Workspace\Dev_space\Code\Python\Anlysis_Agent\NEURAL_BET"
Set-Location $projectPath
& ".\venv\Scripts\Activate.ps1"
python -m src.tui
