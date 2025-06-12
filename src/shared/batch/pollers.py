# import clickhouse_connect
import re
import datetime as dt
import json

# Poller Inputs:
# - config: dict
# - filename: str

# Poller Results:
# - file_date: dt.datetime
# - ?poller: {cursor: DBCursor}

class ItemPoller:
    def download(self, context):
        pass


class DBCursor:
    # def fetchmany(self, chunk_limit):
    #     return None

    def get_columns(self):
        return None

    def on_next(self, callback):
        pass

    def subscribe(self):
        pass



class ClickhouseCursor(DBCursor):
    def __init__(self, stream, columns, chunk_limit):
        self.stream = stream
        self.chunk_limit = chunk_limit
        self.on_next_callback = None
        
    def get_columns(self):
        return None

    def on_next(self, callback):
        self.on_next_callback = callback

    def subscribe(self):
        with self.stream:
            counter = 0
            for block in self.stream:
                counter += 1
                print(f"cursor {counter}: {len(block)}")
                self.on_next_callback(block)

class PostgresCursor(DBCursor):
    def __init__(self, db, query, params, chunk_limit):
        self.db = db
        self.query = query
        self.params = params
        self.chunk_limit = chunk_limit
        self.columns = None
        self.on_next_callback = None
        
    def get_columns(self):
        return self.columns

    def on_next(self, callback):
        self.on_next_callback = callback

    def subscribe(self):
        with self.db.cursor() as cursor:
            cursor.execute(self.query, self.params)
            self.columns = [col[0] for col in cursor.description]
            counter = 0
            while True:
                block = cursor.fetchmany(self.chunk_limit)
                if not block:
                    break
                counter += 1
                print(f"cursor {counter}: {len(block)}")
                self.on_next_callback(block)

class OracleCursor(PostgresCursor):
    pass


# database pollers

class ClickhousePoller:
    def __init__(self, ch):
        self.ch = ch

    def download(self, context):
        config = context['config']

        pattern = re.compile(config['file_pattern'])
        str_date = pattern.search(context['filename']).group(1)
        context['file_date'] = dt.datetime.strptime(str_date, config['file_date_format'])

        params = {
            'fecha_ini': context['file_date'],
            'fecha_fin': context['file_date'] + dt.timedelta(**json.loads(config['loop_time']))
        }
        columns = [col for col in self.ch.query(f"{config['src_query']} limit 1", parameters=params).column_names]
        stream = self.ch.query_row_block_stream(config['src_query'], parameters=params)
        cursor = ClickhouseCursor(stream, columns, context['config']['chunk_limit'])

        context['poller'] = {
            'cursor': cursor,
            'columns': columns
        }

class DatabasePoller:
    def __init__(self, db):
        self.db = db

    def download(self, context):
        config = context['config']

        pattern = re.compile(config['file_pattern'])
        str_date = pattern.search(context['filename']).group(1)
        context['file_date'] = dt.datetime.strptime(str_date, config['file_date_format'])

        params = {
            'fecha_ini': context['file_date'],
            'fecha_fin': context['file_date'] + dt.timedelta(**json.loads(config['loop_time']))
        }
        cursor = self._create_cursor(config['src_query'], params, context['config']['chunk_limit'])

        context['poller'] = {
            'cursor': cursor,
            # 'columns': columns
        }

        print(f"{config['name']}: {str_date}")

    def _create_cursor(self, query, params, chunk_limit):
        pass


class PostgresPoller(DatabasePoller):
    def _create_cursor(self, query, params, chunk_limit):
        return PostgresCursor(self.db, query, params, chunk_limit)

class OraclePoller(DatabasePoller):
    def _create_cursor(self, query, params, chunk_limit):
        return OracleCursor(self.db, query, params, chunk_limit)


class SftpPoller(ItemPoller):
    def __init__(self, sftp_service):
        self.sftp_service = sftp_service

    def download(self, context):
        config = context['config']
        self.sftp_service.useConnection(config['server_id'])
        sftp = self.sftp_service.getReference()
        
        pattern = re.compile(config['file_pattern'])
        str_date = pattern.search(context['filename']).group(1)
        context['file_date'] = dt.datetime.strptime(str_date, config['file_date_format'])

        try:
            print(context['filename'])
            sftp.get(f"{config['work_dir']}/{context['filename']}", f"{context['storage_dir']}/{context['filename']}")
            context['poller'] = {}
        except Exception as e:
            raise e