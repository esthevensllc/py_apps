from src.shared.batch.domain import ItemWriter
import cx_Oracle
import datetime as dt

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
        params = {}
        for field in delete_fields:
            params[f"p_{field['fieldname']}"] = field['reload_argument'].format(**context)
            if field['type'] == 'date':
                params[f"p_{field['fieldname']}"] = dt.datetime.strptime(params[f"p_{field['fieldname']}"], '%Y-%m-%d %H:%M:%S')
        str_delete_fields = " and ".join(list(map(lambda field: f"{field['fieldname']} = :p_{field['fieldname']}", delete_fields)))
        template = f"delete from {tablename} where "+str_delete_fields

        query_validation = f"select count(*) from {tablename} where {str_delete_fields}"
        if context['config'].get('reload_validation', True):
            validation_count = self._fetch(query_validation, params)[0][0]
            print(f"validation_count: {validation_count}")
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
