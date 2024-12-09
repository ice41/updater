@echo off
:: Caminho base relativo ao local do script
set "base_path=WS\Content\Paks\WS-WindowsNoEditor.7z.001"

:: Diretório de saída
set "output_dir=WS\Content\Paks\"

:: Caminho para o 7-Zip e WinRAR
set "7zip_path=C:\Program Files\7-Zip\7z.exe"
set "winrar_path=C:\Program Files\WinRAR\WinRAR.exe"

:: Verificar se o arquivo base existe
if not exist "%base_path%" (
    echo Arquivo base "%base_path%" não encontrado! Verifique o caminho e tente novamente.
    pause
    exit /b
)

:: Verificar se o 7-Zip está disponível
if exist "%7zip_path%" (
    echo Usando 7-Zip para extrair os arquivos segmentados...
    "%7zip_path%" x "%base_path%" -o"%output_dir%"
    if %errorlevel% neq 0 (
        echo Erro ao extrair com o 7-Zip. Verifique os arquivos e tente novamente.
        pause
        exit /b
    )
    echo Extração concluída com sucesso usando 7-Zip!
) else if exist "%winrar_path%" (
    echo Usando WinRAR para extrair os arquivos segmentados...
    "%winrar_path%" x "%base_path%" "%output_dir%"
    if %errorlevel% neq 0 (
        echo Erro ao extrair com o WinRAR. Verifique os arquivos e tente novamente.
        pause
        exit /b
    )
    echo Extração concluída com sucesso usando WinRAR!
) else (
    echo Nenhum programa de extração encontrado (7-Zip ou WinRAR). Instale um deles e tente novamente.
    pause
    exit /b
)

:: Iniciar o jogo após a extração
echo Iniciando o jogo...
START "" ".\WS\Binaries\Win64\WS-Win64-Shipping.exe" StartMenu -game -StableNullID -online=Steam -d3d12 -nosoulmasksession"

pause
