from __future__ import annotations
import datetime
import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
import sys

PY_APPS_DIR = "/opt/airflow/tareas/py_apps"
sys.path.append(PY_APPS_DIR)

from src.shared.app.AppContainer import AppContainer

def execute_procedure(**kwargs):
    app = AppContainer()
    oracle = app.getInstance("dboracle")
    oracle.query("""declare
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
    
        --UTIL
        PK_APIC_CARGA.SP_CHRG_INTRFCS_APIC_UTIL_HXH(v_fecha_ini_hxh_str, v_fecha_fin_hxh_str);
        PK_APIC_CARGA.SP_CHRG_INTRFCS_APIC_UTIL_DIA_RCRR(v_fecha_ini_dia_str, v_fecha_fin_dia_str);
    end;""", {})

with DAG(
    dag_id="apic_stats",
    schedule="15 * * * *",
    start_date=pendulum.datetime(2023, 5, 17, 9, tz="America/Lima"),
    catchup=False,
    tags=["stats", "apic", "prod"],
    default_args={"retries": 1}
) as dag:
    task1 = BashOperator(
        task_id="LoadHardwareUsage",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.apic.nodes.services.LoadHardwareUsage",
    )
    task2 = BashOperator(
        task_id="LoadPCInterfacesTraffic",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.apic.pc_interfaces.services.LoadPCInterfacesTraffic",
    )
    task3 = BashOperator(
        task_id="LoadInterfaceEvents",
        bash_command=f"python {PY_APPS_DIR}/main_unique.py src.apic.interfaces.services.LoadInterfaceEvents",
    )
    task4 = PythonOperator(
        task_id="oracle_handlers",
        python_callable=execute_procedure
    )
    task1 >> task2 >> task3 >> task4