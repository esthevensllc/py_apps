user=smart
pass='Sm4rt12$$'
conn=SMART_FC

$ORACLE_HOME/bin/sqlplus $user/$pass@$conn <<SCRIPT
begin
PK_PADM_QUEUE.SP_MED_HUAWEI2_PRODUCER;
end;
/
SCRIPT

count_process=$(ps -aux | grep src.med_huawei2.mediciones.MedHuawei2EventConsumer | wc -l)
count_process=$((count_process-1))
if [ $count_process -lt 1 ]; then
/index1/tareas/proyectos_python/apps/py_apps/shell/shared/main.sh src.med_huawei2.mediciones.MedHuawei2EventConsumer
fi
/index1/tareas/proyectos_python/apps/py_apps/shell/shared/main.sh src.control_carga.ora_handlers.LoadOracleHandlers med_huawei2
