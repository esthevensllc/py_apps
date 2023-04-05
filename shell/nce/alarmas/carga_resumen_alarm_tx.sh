var_fecha_ini=`date +%d/%m/%Y_%H:%M:%S`

echo ">>>>>>>>>>>>>>>>>>Inicio Proceso de Carga Resumenes ............!!!!!!!"

$ORACLE_HOME/bin/sqlplus smart/'Sm4rt12$$'@SMART_FC <<FIN
BEGIN
    PK_ALARM_HUAWEI_TX.SP_Ejecutar_Resumenes_TX;
END;
/
FIN


var_fecha_fin=`date +%d/%m/%Y_%H:%M:%S`

echo "inicio: ${var_fecha_ini} - fin: ${var_fecha_fin}"
echo ">>>>>>>>>>>>>>>>>>Fin Proceso de Carga Resumenes ............!!!!!!!"
