@echo off
:: Define o caminho base para os arquivos segmentados
set "base_path=WS/Content/Paks/WS-WindowsNoEditor.7z"

:: Caminho para o 7-Zip. Altere se necessário.
set "7zip_path=C:\Program Files\7-Zip\7z.exe"

:: Comando para extrair os arquivos
"%7zip_path%" x "%base_path%.001" -oWS/Content/Paks/

:: Verifica se a extração foi bem-sucedida
if %errorlevel% equ 0 (
    echo Extração concluída com sucesso!
) else (
    echo Ocorreu um erro durante a extração.
)
START "" ".\WS\Binaries\Win64\WS-Win64-Shipping.exe" StartMenu -game -StableNullID -online=Steam -d3d12 -nosoulmasksession
pause

EXIT
