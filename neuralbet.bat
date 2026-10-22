@echo off
:: NEURAL BET - Global Launch Script
:: Add this folder to your PATH to run 'neuralbet' from anywhere

cd /d "c:\Users\LEANDRE\Workspace\Dev_space\Code\Python\Anlysis_Agent\NEURAL_BET"
call .\venv\Scripts\activate
python -m src.tui
