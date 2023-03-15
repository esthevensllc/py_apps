user=smart
pass='Sm4rt12$$'
conn=SMART_FC

#inicio
var_fecha_ini=`date +%d/%m/%Y' '%H:%M:%S`

$ORACLE_HOME/bin/sqlplus $user/$pass@$conn <<SCRIPT
declare
    v_fecha_fin date := sysdate;
    v_fecha_ini date := v_fecha_fin - interval '3' hour;
    v_fecha_ini_hxh_str varchar2(50) := to_char(v_fecha_ini, 'dd/mm/yyyy hh24');
    v_fecha_fin_hxh_str varchar2(50) := to_char(v_fecha_fin, 'dd/mm/yyyy hh24');
    v_fecha_ini_dia_str varchar2(50) := '';
    v_fecha_fin_dia_str varchar2(50) := '';
begin
    v_fecha_ini := v_fecha_fin - interval '2' day;
    v_fecha_ini_dia_str := to_char(v_fecha_ini, 'dd/mm/yyyy');
    v_fecha_fin_dia_str := to_char(v_fecha_fin, 'dd/mm/yyyy');

    begin
        sp_chrg_tx_arbor_type_dia(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        sp_chrg_tx_arbor_name_dia(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        sp_chrg_tx_arbor_impacto_mes(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        sp_chrg_tx_arbor_varios_hxh(v_fecha_ini_hxh_str, v_fecha_fin_hxh_str);
        sp_chrg_tx_arbor_varios_dia(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        sp_chrg_tx_arbor_varios_mes(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
    end;
end;
/
SCRIPT

var_fecha_fin=`date +%d/%m/%Y' '%H:%M:%S`

echo "Fecha inicio fin: ${var_fecha_ini} - ${var_fecha_fin}"
