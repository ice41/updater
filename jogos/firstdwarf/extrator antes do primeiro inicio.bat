@echo off
setlocal

rem Definindo os caminhos dos arquivos
set arquivo1="%~dp0First Dwarf\FirstDwarf\Content\Movies\intro.7z.001"
set arquivo2="%~dp0First Dwarf\FirstDwarf\Binaries\Win64\FirstDwarf-Win64-Shipping.7z"

rem Definindo os caminhos das pastas de destino (mesmas pastas onde estão os arquivos)
set pasta_destino1="%~dp0First Dwarf\FirstDwarf\Content\Movies"
set pasta_destino2="%~dp0First Dwarf\FirstDwarf\Binaries\Win64"

rem Tentar usar 7-Zip se estiver instalado
if exist "C:\Program Files\7-Zip\7z.exe" (
    echo Usando 7-Zip para extrair arquivos...
    "C:\Program Files\7-Zip\7z.exe" x %arquivo1% -o%pasta_destino1%
    "C:\Program Files\7-Zip\7z.exe" x %arquivo2% -o%pasta_destino2%
) else (
    echo 7-Zip não encontrado. Tentando usar WinRAR...
    echo instale o 7-zip é free e melhor que o winrar...
)

rem Usar WinRAR para extrair arquivos
if exist "C:\Program Files\WinRAR\WinRAR.exe" (
    echo Usando WinRAR para extrair arquivos...
    "C:\Program Files\WinRAR\WinRAR.exe" x -o+ %arquivo1% %pasta_destino1%
    "C:\Program Files\WinRAR\WinRAR.exe" x -o+ %arquivo2% %pasta_destino2%
) else (
    echo Nenhum dos programas está instalado. Não foi possível extrair os arquivos.
)

echo Extração concluída.
pause
endlocal
