# Top IPs CGNAT hacia ClickHouse elog

Este proyecto ejecuta cuatro consultas sobre cada nodo ClickHouse CGNAT y carga
los resultados del día anterior en cuatro tablas de `elog`:

| Consulta | Tabla destino |
|---|---|
| Top IPs destino sin DNS por uso | `Top_IPs_Dst_NO_DNS` |
| Top IPs privadas con destino DNS por uso | `Top_IPs_Priv_con_Dst-DNS` |
| Top IPs privadas por puerto SMTP 25 | `Top_IPs_Priv_SMTP_25` |
| Top IPs privadas por uso distinto de SMTP 25 | `Top_IPs_Priv_Uso` |

Cada consulta se realiza en los cuatro nodos configurados. Las tablas incluyen
las catorce columnas solicitadas, más `fecha_proceso` y `nodo_origen`. Esos dos
campos permiten identificar el origen y reemplazar de forma segura una fecha al
reintentar el DAG.

## Configuración

La configuración está aislada en `src/top_ips_elog/.env`. Copie
`.env.example` como base y complete las credenciales de origen y destino.

El usuario destino necesita permisos `CREATE TABLE`, `ALTER DELETE` e `INSERT`
en el esquema `elog`. Las tablas se crean automáticamente a partir del esquema
de `cgnat.huawei_cgn_nat_v2_YYYY_MM_DD` si todavía no existen.

## Ejecución

Desde la raíz del repositorio:

```bash
python -m src.top_ips_elog
```

El proceso toma por defecto ayer en America/Lima. Para una fecha concreta:

```bash
python -m src.top_ips_elog --process-date 2026-09-08
```

El DAG `dags/top_ips_elog.py` se ejecuta todos los días a las 05:00
America/Lima. El valor de `TOP_IPS_PROCESS_DATE` se calcula desde el intervalo
del DAG, por lo que procesa el día calendario anterior incluso al reintentar.
