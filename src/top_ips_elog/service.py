import datetime as dt
import json


class TopIpsElogLoadService:
    def __init__(self, sources, target_repository, definitions):
        if not sources:
            raise ValueError('Debe configurarse al menos un nodo ClickHouse origen')
        self.sources = list(sources)
        self.target_repository = target_repository
        self.definitions = list(definitions)

    def execute(self, process_date: dt.date):
        source_schema = self._validate_source_schemas(process_date)
        results = {}
        for definition in self.definitions:
            print(f'TOP_QUERY_START key={definition.key} table={definition.target_table} process_date={process_date.isoformat()}')
            self.target_repository.ensure_table(definition.target_table, source_schema)
            self.target_repository.delete_process_date(definition.target_table, process_date)
            result = self._load_definition(definition, process_date)
            results[definition.key] = result
            print('TOP_QUERY_RESULT ' + json.dumps(result, sort_keys=True))
        summary = {
            'status': 'SUCCESS',
            'process_date': process_date.isoformat(),
            'query_count': len(results),
            'inserted_rows': sum(result['inserted_rows'] for result in results.values()),
            'queries': results,
        }
        print('TOP_LOAD_RESULT ' + json.dumps(summary, sort_keys=True))
        return summary

    def _validate_source_schemas(self, process_date: dt.date):
        reference_schema = None
        for host, repository in self.sources:
            schema = repository.describe(process_date)
            if reference_schema is None:
                reference_schema = schema
            elif schema != reference_schema:
                raise RuntimeError(f'El esquema de {host} no coincide con el del primer nodo para la tabla del día solicitado')
            print(f'TOP_SCHEMA_OK host={host} columns={len(schema)} process_date={process_date.isoformat()}')
        return reference_schema

    def _load_definition(self, definition, process_date: dt.date):
        per_host, total = {}, 0
        for host, repository in self.sources:
            print(f'TOP_SOURCE_START key={definition.key} host={host}')
            rows = repository.fetch_top_rows(definition, process_date)
            inserted = self.target_repository.insert_rows(definition.target_table, rows, process_date, host)
            result = {'host': host, 'source_rows': len(rows), 'inserted_rows': inserted}
            per_host[host] = result
            total += inserted
            print('TOP_SOURCE_RESULT ' + json.dumps(result, sort_keys=True))
        return {
            'key': definition.key,
            'target_table': definition.target_table,
            'process_date': process_date.isoformat(),
            'inserted_rows': total,
            'sources': per_host,
        }
