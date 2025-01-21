#!/bin/sh

# p_formato_archivo="$1"

# ruta completa del archivo ejemplo: /voltage/MMLTask_VALORES_VOLTAJE_20250105_050006.txt
p_archivo="$1"
# ruta de trabajo ejemplo: /voltage/temp
p_ruta_estadisticas="$2"

p_ruta_bloques=$p_ruta_estadisticas/bloques
p_ruta_files=$p_ruta_estadisticas/files

# Elimiando la ruta de bloques y archivos
if [ -d "$p_ruta_estadisticas" ]; then
    rm -rf $p_ruta_estadisticas
fi
if [ -d "$p_ruta_bloques" ]; then
    rm -rf $p_ruta_bloques
fi
if [ -d "$p_ruta_bloques" ]; then
    rm -rf $p_ruta_bloques
fi

#echo elimino las carpteas
# Creando la ruta de bloques y archivos
mkdir $p_ruta_estadisticas
mkdir $p_ruta_bloques
mkdir $p_ruta_files

# Divdiendo el archivo en bloques
awk '/=============================================================/{flag=1; filename="'$p_ruta_bloques/bloque_'"NR".txt"}; flag{print >filename}' $p_archivo

echo Se generaron los bloques satisfactoriamente

# Capturando los archivos de bloques
v_bloques=$(ls $p_ruta_bloques/*)

# Dividiendo los bloques por elemento 
for bloque in $v_bloques
do
    #echo procesando: $bloque
    tp_filename=$(basename "$bloque")
    tp_filename="${tp_filename%.*}"
    awk '/NE Name:/{flag=1; filename="'$p_ruta_files/${tp_filename}_file_'"NR".txt"}; flag{print >filename}' $bloque
done

echo Se dividieron los bloques por elemento satisfactoriamente

v_cantidad_archivos=$(ls $p_ruta_files | wc -l)
echo Cantidad de archivos generados: $v_cantidad_archivos

# Eliminando los archivos que no tienen informacion
filenames=$(grep -Rl "$p_ruta_files" -e 'Failed to query NE information' -e 'Ne is not connected' -e 'Invalid command,it is inexecutable' -e 'No matching result is found' -e 'NE response time out.' -e 'NE is not connected.')

for file in $filenames
do
    rm -rf  $file
done

v_cantidad_archivos=$(ls $p_ruta_files | wc -l)
echo "Cantidad de archivos despues de eliminar los que no tiene mediciones: $v_cantidad_archivos"

rm -rf $p_ruta_files/nr1
rm -rf $p_ruta_files/nr2
rm -rf $p_ruta_files/nr3

mkdir $p_ruta_files/nr1
mkdir $p_ruta_files/nr2
mkdir $p_ruta_files/nr3

files_nr3=$(grep -l -P 'To be continued...' "$p_ruta_files"/*.txt)

for file in $files_nr3
do
    mv "$file" $p_ruta_files/nr3
    rm -rf "$file"
done

files_nr2=$(grep -l -P '(Number of results = ([2-9]|[1-9][0-9]+))' "$p_ruta_files"/*.txt)

echo $files_nr2 > $p_ruta_estadisticas/test_nr2.txt

for file in $files_nr2
do
    mv "$file" $p_ruta_files/nr2
    rm -rf "$file"
done

files_nr1=$(grep -l "$p_ruta_files"/*.txt -e '(Number of results = 1)')

for file in $files_nr1
do
    mv "$file" $p_ruta_files/nr1
    rm -rf "$file"
done

rm -rf $p_ruta_bloques