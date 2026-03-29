@echo off
title KoboldCPP - Motor LLM Vulkan (AMD RX 7600)
echo Iniciando o Llama 3.1 no FELPINHO's RPG ENGINE...

:: O comando abaixo aponta para a pasta models onde o arquivo GGUF está guardado
koboldcpp.exe --usevulkan --gpulayers 33 --contextsize 8192 --port 5001 models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf

pause