@echo off
:: Definir o caminho base para os arquivos segmentados
set "base_path=WS/Content/Paks/WS-WindowsNoEditor.7z"

:: Caminho para o WinRAR ou 7-Zip. Atualize se necessário.
set "winrar_path=C:\Program Files\WinRAR\WinRAR.exe"
set "7zip_path=C:\Program Files\7-Zip\7z.exe"

:: Diretório de saída
set "output_dir=WS/Content/Paks/"

:: Verifica se o 7-Zip está disponível
if exist "%7zip_path%" (
    echo Usando 7-Zip para extrair os arquivos...
    "%7zip_path%" x "%base_path%.001" -o"%output_dir%"
    set "extractor=7-Zip"
) else (
    :: Se o 7-Zip não está disponível, tenta o WinRAR
    if exist "%winrar_path%" (
        echo Usando WinRAR para extrair os arquivos...
        "%winrar_path%" x "%base_path%.001" "%output_dir%"
        set "extractor=WinRAR"
    ) else (
        echo Nenhum programa de extração encontrado (7-Zip ou WinRAR)!
        pause
        exit /b
    )
)

:: Verificar se a extração foi bem-sucedida
if %errorlevel% neq 0 (
    echo Ocorreu um erro durante a extração com %extractor%.
    pause
    exit /b
) else (
    echo Extração concluída com sucesso usando %extractor%!
)

:: Iniciar o jogo
echo Iniciando o jogo...
START "" ".\WS\Binaries\Win64\WS-Win64-Shipping.exe" StartMenu -game -StableNullID -online=Steam -d3d12 -nosoulmasksession"

pause
