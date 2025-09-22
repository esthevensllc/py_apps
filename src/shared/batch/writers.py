from src.shared.batch.domain import ItemWriter
import cx_Oracle
import datetime as dt
import json
from src.shared.database.ClickHouseDB import ClickHouseDB

class OracleWriter(ItemWriter):
    def __init__(self, db, control_repo):
        self.db = db
        self.control_repo = control_repo
        self.context = None
        self.fieldtypes = {
            'number': cx_Oracle.NUMBER,
            'date': cx_Oracle.DATETIME,
            'int': cx_Oracle.NUMBER,
            'varchar2': cx_Oracle.STRING,
            'clob': cx_Oracle.CLOB
        }
        self.template = None
        self.bindings = []
        self.start_time = None
        self.counter = 0

    def start(self, context: dict):
        self.context = context
        self.counter = 0
        self.start_time = dt.datetime.now()
        self.template, self.bindings = self._get_template_binds()
        self._delete_data(context)

    def _delete_data(self, context):
        fields = context['config']['fields']
        tablename = context['config']['tablename']
        delete_fields = list(filter(lambda f: f.get('to_reload') == 1, fields))
        if len(delete_fields) == 0:
            raise Exception("No existen campos delimitados para recargar")
        params = {}
        str_filters = []
        for field in delete_fields:
            if field['type'] == 'date':
                params[f"p_{field['fieldname']}_ini"] = field['reload_argument'].format(**context)
                params[f"p_{field['fieldname']}_ini"] = dt.datetime.strptime(params[f"p_{field['fieldname']}_ini"], '%Y-%m-%d %H:%M:%S')
                params[f"p_{field['fieldname']}_fin"] = params[f"p_{field['fieldname']}_ini"] + dt.timedelta(**json.loads(context['config']['loop_time']))
                str_filters.append(f"{field['fieldname']} >= :p_{field['fieldname']}_ini and {field['fieldname']} < :p_{field['fieldname']}_fin")
            else:
                params[f"p_{field['fieldname']}"] = field['reload_argument'].format(**context)
                str_filters.append(f"{field['fieldname']} = :p_{field['fieldname']}")
        str_delete_fields = " and ".join(str_filters)
        template = f"delete from {tablename} where "+str_delete_fields

        query_validation = f"select count(*) from {tablename} where {str_delete_fields}"
        if context['config'].get('reload_validation', True):
            validation_count = self._fetch(query_validation, params)[0][0]
            # print(f"validation_count: {validation_count}")
            if validation_count > 0:
                print(f"deleting")
                self._execute(template, params)
        else:
            print(f"deleting")
            self._execute(template, params)

    def _fetch(self, query, params):
        with self.db.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def _execute(self, query, params):
        with self.db.cursor() as cursor:
            cursor.execute(query, params)
            self.db.commit()

    def write(self, items):
        cursor = self.db.cursor()
        cursor.setinputsizes(*self.bindings)

        cursor.prepare(self.template)
        cursor.executemany(None, items, batcherrors=True)

        str_error = None
        for error in cursor.getbatcherrors():
            str_error = error
        cursor.close()

        if str_error is not None:
            raise Exception(str_error)
        self.counter += len(items)

    def _get_template_binds(self):
        fieldtypes = self.fieldtypes
        str_fields = []
        str_binds = []
        bindings = []
        for field in self.context['config']['fields']:
            if field is not None:
                str_fields.append(field['fieldname'])
                str_binds.append(f":{field['fieldname']}")
                cx_oracle_type = None
                if field['type'] == 'number' or field['type'] == 'int':
                    cx_oracle_type = fieldtypes[field['type']]
                elif field['type'] == 'varchar2':
                    cx_oracle_type = fieldtypes[field['type']]
                elif field['type'] == 'clob':
                    cx_oracle_type = fieldtypes[field['type']]
                elif field['type'] == 'date':
                    cx_oracle_type = fieldtypes[field['type']]
                else:
                    raise Exception(f"El field {field['fieldname']} tiene un tipo de dato '{field['type']}' que no existe")
                bindings.append(cx_oracle_type)

        template = f"INSERT INTO {self.context['config']['tablename']}({', '.join(str_fields)}) VALUES ({', '.join(str_binds)})"
        return template, bindings
    
    def complete(self):
        self.db.commit()
        self._save_control_file(None)
        print("data:", self.counter)

        if self.context['config'].get('exec_after_st') is not None:
            to_execute = self.context['config']['exec_after_st'].format(**self.context)
            self._execute(to_execute, {})

    def error(self, e):
        self.db.rollback()
        self._save_control_file(e)

    def _save_control_file(self, error):
        if self.context is not None:
            config = self.context['config']
            end_time = dt.datetime.now()
            self.control_repo.save_carga(
                config['queue_id'],
                self.context['filename'],
                self.counter,
                self.context['file_count'],
                self.start_time,
                end_time,
                'CARGADO' if error is None else 'ERROR',
                str(error) if error is not None else None,
                self.context['file_date']
            )


class ClickhouseWriter(ItemWriter):
    def __init__(self, db):
        self.db = db
        self.context = None
        self.fieldtypes = {
            'number': ClickHouseDB.DECIMAL,
            'date': ClickHouseDB.DATETIME,
            'int': ClickHouseDB.INTEGER,
            'varchar2': ClickHouseDB.STRING,
        }
        self.template = None
        self.bindings = []
        self.start_time = None
        self.counter = 0

    def start(self, context: dict):
        self.context = context
        self.counter = 0
        self.start_time = dt.datetime.now()
        self.template, self.bindings = self._get_template_binds()
        self._delete_data(context)

    def _delete_data(self, context):
        fields = context['config']['fields']
        tablename = context['config']['tablename']
        delete_fields = list(filter(lambda f: f.get('to_reload') == 1, fields))
        if len(delete_fields) == 0:
            raise Exception("No existen campos delimitados para recargar")
        params = {}
        str_filters = []
        for field in delete_fields:
            if field['type'] == 'date':
                params[f"p_{field['fieldname']}_ini"] = field['reload_argument'].format(**context)
                params[f"p_{field['fieldname']}_ini"] = dt.datetime.strptime(params[f"p_{field['fieldname']}_ini"], '%Y-%m-%d %H:%M:%S')
                params[f"p_{field['fieldname']}_fin"] = params[f"p_{field['fieldname']}_ini"] + dt.timedelta(**json.loads(context['config']['loop_time']))
                # str_filters.append(f"{field['fieldname']} >= :p_{field['fieldname']}_ini and {field['fieldname']} < :p_{field['fieldname']}_fin")
                str_filters.append(f"{field['fieldname']} >= {{p_{field['fieldname']}_ini:DateTime}} and {field['fieldname']} < {{p_{field['fieldname']}_fin:DateTime}}")
            else:
                params[f"p_{field['fieldname']}"] = field['reload_argument'].format(**context)
                str_filters.append(f"{field['fieldname']} = {{p_{field['fieldname']}:String}}")
                # str_filters.append(f"{field['fieldname']} = :p_{field['fieldname']}")
        str_delete_fields = " and ".join(str_filters)
        template = f"alter table {tablename} delete where "+str_delete_fields

        query_validation = f"select count(*) from {tablename} where {str_delete_fields}"
        if context['config'].get('reload_validation', True):
            validation_count = self._fetch(query_validation, params)[0][0]
            # print(f"validation_count: {validation_count}")
            if validation_count > 0:
                print(f"deleting")
                self._execute(template, params)
        else:
            print(f"deleting")
            self._execute(template, params)

    def _fetch(self, query, params):
        result = self.db.query(query, parameters=params)
        return result.result_rows

    def _execute(self, query, params):
        self.db.command(query, parameters=params)

    def write(self, items):
        self.db.insert(self.template, items, column_names=self.bindings)
        self.counter += len(items)

    def _get_template_binds(self):
        fieldtypes = self.fieldtypes
        str_fields = []
        str_binds = []
        bindings = []
        for field in self.context['config']['fields']:
            if field is not None:
                str_fields.append(field['fieldname'])
                str_binds.append(f":{field['fieldname']}")
                cx_oracle_type = None
                if field['type'] == 'number' or field['type'] == 'int':
                    cx_oracle_type = fieldtypes[field['type']]
                elif field['type'] == 'varchar2':
                    cx_oracle_type = fieldtypes[field['type']]
                elif field['type'] == 'clob':
                    cx_oracle_type = fieldtypes[field['type']]
                elif field['type'] == 'date':
                    cx_oracle_type = fieldtypes[field['type']]
                else:
                    raise Exception(f"El field {field['fieldname']} tiene un tipo de dato '{field['type']}' que no existe")
                bindings.append(field['fieldname'])

        template = self.context['config']['tablename']
        return template, bindings
    
    def complete(self):
        print("data:", self.counter)

    def error(self, e):
        pass


class ControlCargaWriter(ItemWriter):
    def __init__(self, control_repo):
        self.control_repo = control_repo
        self.start_time = None
        self.context = None

    def start(self, context):
        self.context = context
        self.counter = 0
        self.start_time = dt.datetime.now()

    def write(self, items):
        self.counter += len(items)

    def complete(self):
        self._save_control_file(None)

    def error(self, e):
        self._save_control_file(e)

    def _save_control_file(self, error):
        if self.context is not None:
            config = self.context['config']
            end_time = dt.datetime.now()
            self.control_repo.save_carga(
                config['queue_id'],
                self.context['filename'],
                self.counter,
                self.context['file_count'],
                self.start_time,
                end_time,
                'CARGADO' if error is None else 'ERROR',
                str(error) if error is not None else None,
                self.context['file_date']
            )


class OracleScriptExecutor(ItemWriter):
    def __init__(self, db):
        self.db = db
        self.start_time = None

    def start(self, context):
        self.context = context
        self.counter = 0
        self.start_time = dt.datetime.now()

        if self.context['config'].get('exec_before_st') is not None:
            to_execute = self.context['config']['exec_before_st'].format(**self.context)
            self._execute(to_execute, {})

    def write(self, items):
        pass

    def complete(self):
        if self.context['config'].get('exec_after_st') is not None:
            to_execute = self.context['config']['exec_after_st'].format(**self.context)
            self._execute(to_execute, {})

    def error(self, e):
        pass

    def _execute(self, query, params):
        with self.db.cursor() as cursor:
            cursor.execute(query, params)
            self.db.commit()

