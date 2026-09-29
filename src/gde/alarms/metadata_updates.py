"""Actualiza datos de gestión de alarmas ya cargadas desde GDE."""

import datetime as dt
import time


class GdeMetadataUpdater:
    PAGE_SIZE = 30000
    LOOKBACK_MINUTES = 180
    MAX_API_ATTEMPTS = 3
    IDENTITY_FIELDS = (
        "alarmserialnumber",
        "alarmname",
        "alarmid",
        "node",
        "emsname",
        "firstoccurrence",
    )

    def __init__(self, db, api, repository):
        self.db = db
        self.api = api
        self.repository = repository

    def execute(self):
        config = self.repository.find("1")
        if config is None or config["status"] != 1:
            raise ValueError("La carga GDE no está activa")

        # La misma fecha se usa en las dos consultas, en el huso horario del
        # proceso, igual que las solicitudes actuales de alarmas GDE.
        date = dt.datetime.now().strftime("%Y-%m-%d %H:%M:00")
        remark_rows = self._fetch_rows(config["api_query"], date, "last_remark_update_time")
        remedy_rows = self._fetch_rows(config["api_query"], date, "last_remedy_update_time")
        remark_updates = self._prepare_updates(remark_rows, "remark", "last_remark_update_time")
        remedy_updates = self._prepare_updates(remedy_rows, "remedy_id", "last_remedy_update_time")

        connection = self.db.getReference()
        cursor = connection.cursor()
        try:
            remark_count = self._update_field(cursor, "remark", remark_updates)
            remedy_count = self._update_field(cursor, "remedy_id", remedy_updates)
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            cursor.close()

        print(
            f"GDE_METADATA_COMPLETE date={date} "
            f"remark_received={len(remark_rows)} remark_matched={remark_count} "
            f"remedy_received={len(remedy_rows)} remedy_matched={remedy_count}"
        )

    def _fetch_rows(self, uri, date, configured_field):
        base_params = {
            "date": date,
            "substract_minutes": self.LOOKBACK_MINUTES,
            "configured_field": configured_field,
            "limit": self.PAGE_SIZE,
            "start": 0,
        }
        for attempt in range(1, self.MAX_API_ATTEMPTS + 1):
            if attempt > 1:
                time.sleep(1)
            params = base_params.copy()
            rows = []
            total = None
            previous_page = None
            short_page_probe = False
            while True:
                result = self.api.get(uri, params).json()
                page = result.get("results")
                if not isinstance(page, list):
                    raise ValueError(f"GDE no devolvió results para {configured_field}")
                if len(page) > self.PAGE_SIZE:
                    raise ValueError(f"GDE devolvió más de {self.PAGE_SIZE} filas para {configured_field}")
                if result.get("total") is not None:
                    total = int(result["total"])
                    if total < 0:
                        raise ValueError(f"GDE devolvió un total negativo para {configured_field}")
                if params["start"] > 0 and total is not None and len(page) >= total:
                    print(
                        f"GDE_METADATA_SNAPSHOT field={configured_field} date={date} "
                        f"start={params['start']} rows={len(page)} total={total}; "
                        "se usa esta respuesta completa"
                    )
                    return page
                if params["start"] > 0 and page and page == previous_page:
                    print(f"GDE_METADATA_RETRY field={configured_field} attempt={attempt} repeated_page")
                    break
                rows.extend(page)
                print(
                    f"GDE_METADATA_PAGE field={configured_field} date={date} "
                    f"attempt={attempt} start={params['start']} rows={len(page)} "
                    f"downloaded={len(rows)} total={total}"
                )
                if total is not None and len(rows) >= total:
                    if len(rows) > total:
                        print(
                            f"GDE_METADATA_TOTAL_MISMATCH field={configured_field} "
                            f"received={len(rows)} reported_total={total}; "
                            "se procesan todas las filas recibidas"
                        )
                    return rows
                if len(page) < self.PAGE_SIZE:
                    if total is None:
                        return rows
                    if page and not short_page_probe:
                        short_page_probe = True
                        previous_page = page
                        params["start"] += len(page)
                        print(
                            f"GDE_METADATA_PROBE field={configured_field} "
                            f"attempt={attempt} start={params['start']}"
                        )
                        continue
                    print(
                        f"GDE_METADATA_RETRY field={configured_field} attempt={attempt} "
                        f"received={len(rows)} reported_total={total}"
                    )
                    break
                previous_page = page
                params["start"] += len(page)

        raise RuntimeError(
            f"GDE no completó {configured_field} tras {self.MAX_API_ATTEMPTS} "
            f"consultas desde start=0"
        )

    def _prepare_updates(self, rows, value_field, time_field):
        latest = {}
        for row in rows:
            required = (*self.IDENTITY_FIELDS, value_field, time_field)
            missing = [field for field in required if field not in row]
            if missing:
                raise ValueError(f"Respuesta GDE sin campos {missing} para {value_field}")
            if not row["alarmserialnumber"] or not row["firstoccurrence"]:
                raise ValueError(f"Alarma sin identidad completa para {value_field}")
            firstoccurrence = dt.datetime.fromisoformat(row["firstoccurrence"])
            key = tuple(row[field] for field in self.IDENTITY_FIELDS[:-1]) + (firstoccurrence,)
            update_time = row[time_field] or ""
            previous = latest.get(key)
            if previous is None or update_time >= previous[0]:
                latest[key] = (update_time, row[value_field])

        return [
            dict(zip(self.IDENTITY_FIELDS, key), updated_value=value)
            for key, (_, value) in latest.items()
        ]

    def _update_field(self, cursor, field, updates):
        if not updates:
            return 0
        # Las seis columnas son la misma identidad utilizada por
        # SP_ALARM_AUTIN_GESTOR para sustituir una alarma existente.
        sql = f"""
            UPDATE autin_alarm_gestor t
               SET t.{field} = :updated_value
             WHERE t.alarmserialnumber = :alarmserialnumber
               AND (t.alarmname = :alarmname OR (t.alarmname IS NULL AND :alarmname IS NULL))
               AND (t.alarmid = :alarmid OR (t.alarmid IS NULL AND :alarmid IS NULL))
               AND (t.node = :node OR (t.node IS NULL AND :node IS NULL))
               AND (t.emsname = :emsname OR (t.emsname IS NULL AND :emsname IS NULL))
               AND t.firstoccurrence = :firstoccurrence
        """
        cursor.executemany(sql, updates)
        return cursor.rowcount
