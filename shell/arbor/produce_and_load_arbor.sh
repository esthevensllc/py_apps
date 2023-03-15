user=smart
pass='Sm4rt12$$'
conn=SMART_FC

$ORACLE_HOME/bin/sqlplus $user/$pass@$conn <<SCRIPT
declare
    v_fecha_ini date := trunc(sysdate, 'dd') - interval '1' day;
    v_fecha_fin date := v_fecha_ini + interval '1' day;
    v_format varchar2(10) := 'dxd';
    
    cursor cur_queues is
    select id from padm_queue_config where group_id='arbor' and estado=1;
begin
    for v_row in cur_queues
    loop
        PK_PADM_QUEUE.SP_LOAD_ARBOR(v_row.id, v_fecha_ini, v_fecha_fin, v_format);
    end loop;
end;
/
SCRIPT

sh /index1/tareas/proyectos_python/apps/py_apps/shell/shared/main.sh arbor_async_event_consumer

$ORACLE_HOME/bin/sqlplus $user/$pass@$conn <<SCRIPT
declare
    v_fecha_fin date := trunc(sysdate, 'dd') - interval '1' day;
    v_fecha_ini date := v_fecha_fin - interval '1' day;
    v_fecha_ini_hxh_str varchar2(50) := to_char(v_fecha_ini, 'dd/mm/yyyy hh24');
    v_fecha_fin_hxh_str varchar2(50) := to_char(v_fecha_fin, 'dd/mm/yyyy hh24');
    v_fecha_ini_dia_str varchar2(50) := '';
    v_fecha_fin_dia_str varchar2(50) := '';
begin
    v_fecha_ini := v_fecha_fin - interval '2' day;
    v_fecha_ini_dia_str := to_char(v_fecha_ini, 'dd/mm/yyyy');
    v_fecha_fin_dia_str := to_char(v_fecha_fin, 'dd/mm/yyyy');

    begin
        PK_ARBOR_CARGA.sp_chrg_tx_arbor_type_dia(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        PK_ARBOR_CARGA.sp_chrg_tx_arbor_name_dia(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        PK_ARBOR_CARGA.sp_chrg_tx_arbor_impacto_mes(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        PK_ARBOR_CARGA.sp_chrg_tx_arbor_varios_hxh(v_fecha_ini_hxh_str, v_fecha_fin_hxh_str);
        PK_ARBOR_CARGA.sp_chrg_tx_arbor_varios_dia(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        PK_ARBOR_CARGA.sp_chrg_tx_arbor_varios_mes(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
    end;
end;
/
SCRIPT

