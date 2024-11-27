# import clickhouse_connect
import re
import datetime as dt
import json

class DBCursor:
    def fetchmany(self, chunk_limit):
        return None

    def get_columns(self):
        return None

# class ClickhouseCursor(DBCursor):
#     def __init__(self, result):
#         self.result = result
#         self.columns = [col for col in result.column_names]
#         self.rows = result.result_rows
#         self.len_rows = len(self.rows)
#         self.send_values = True
#         self.counter = 0
#         print(f"cursor total: {len(self.rows)}")
    
#     def fetchmany(self, chunk_limit):
#         if self.len_rows < self.counter+1:
#             return None
#         rows = self.rows[self.counter:self.counter + chunk_limit]
#         print(f"cursor {self.counter}: {len(rows)}")
#         self.counter += chunk_limit
#         return rows
        
#     def get_columns(self):
#         return self.columns


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