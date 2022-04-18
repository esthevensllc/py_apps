user=smart
pass='Sm4rt12$$'
conn=SMART_FC

#inicio
var_fecha_ini=`date +%d/%m/%Y' '%H:%M:%S`

$ORACLE_HOME/bin/sqlplus $user/$pass@$conn <<SCRIPT
declare
    v_event_id number := 0;
    p_msg_body varchar2(250) := '{"groups": ["Balanceadores","ROUTERS CACs","SEDES","CALL CENTERS"]}';
begin
    begin
        select id into v_event_id from padm_queue_events where queue_id = 'pm.int_traffic'
        fetch first 1 rows only;
        
        update padm_queue_events set
        estado=0
        where id = v_event_id;
    exception
        when NO_DATA_FOUND then
        insert into padm_queue_events(QUEUE_ID, MSG_BODY)
        values ('pm.int_traffic', p_msg_body);
    end;
    
    commit;
end;
/
SCRIPT

var_fecha_fin=`date +%d/%m/%Y' '%H:%M:%S`

echo "Fecha inicio fin: ${var_fecha_ini} - ${var_fecha_fin}"
