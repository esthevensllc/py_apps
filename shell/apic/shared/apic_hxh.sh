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
        PK_APIC_CARGA.sp_cm_chrg_tx_acifbrc_cpu_hxh(v_fecha_ini_hxh_str, v_fecha_fin_hxh_str);
        PK_APIC_CARGA.sp_cm_chrg_rss_tx_acifbrc_cpu_hxh(v_fecha_ini_hxh_str, v_fecha_fin_hxh_str);
        PK_APIC_CARGA.sp_cm_chrg_tx_acifbrc_cpu_dia(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        PK_APIC_CARGA.sp_cm_chrg_rss_tx_acifbrc_cpu_dia(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        PK_APIC_CARGA.sp_chrg_tx_rc_acifbrc_cpu_obs(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        PK_APIC_CARGA.sp_chrg_rss_tx_rc_acifbrc_cpu_obs(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
    end;

    --MEMORIA
    begin
        PK_APIC_CARGA.sp_cm_chrg_tx_acifbrc_mem_hxh(v_fecha_ini_hxh_str, v_fecha_fin_hxh_str);
        PK_APIC_CARGA.sp_cm_chrg_rss_tx_acifbrc_mem_hxh(v_fecha_ini_hxh_str, v_fecha_fin_hxh_str);
        PK_APIC_CARGA.sp_cm_chrg_tx_acifbrc_mem_dia(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        PK_APIC_CARGA.sp_cm_chrg_rss_tx_acifbrc_mem_dia(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        PK_APIC_CARGA.sp_chrg_tx_rc_acifbrc_mem_obs(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        PK_APIC_CARGA.sp_chrg_rss_tx_rc_acifbrc_mem_obs(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
    end;

    --TEMPERATURA
    begin
        PK_APIC_CARGA.sp_cm_chrg_tx_rc_acifbrc_temp_hxh(v_fecha_ini_hxh_str, v_fecha_fin_hxh_str);
        PK_APIC_CARGA.sp_cm_chrg_rss_tx_acifbrc_temp_hxh(v_fecha_ini_hxh_str, v_fecha_fin_hxh_str);
        PK_APIC_CARGA.sp_cm_chrg_tx_acifbrc_temp_dia(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        PK_APIC_CARGA.sp_cm_chrg_rss_tx_acifbrc_temp_dia(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        PK_APIC_CARGA.sp_chrg_tx_rc_acifbrc_temp_obs(v_fecha_ini_dia_str, v_fecha_fin_dia_str);---NO SE EN DASH SUPERSET
        PK_APIC_CARGA.sp_chrg_tx_rc_acifbrc_temp_obs_tot(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
        PK_APIC_CARGA.sp_chrg_rss_tx_rc_acifbrc_temp_obs_tot(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
    end;
	
	--TRAFICO
	begin
		PK_APIC_CARGA.sp_chrg_intrfcs_aci_egress_hxh(v_fecha_ini_hxh_str, v_fecha_fin_hxh_str);
	end;
	
end;
/
SCRIPT

var_fecha_fin=`date +%d/%m/%Y' '%H:%M:%S`

echo "Fecha inicio fin: ${var_fecha_ini} - ${var_fecha_fin}"
