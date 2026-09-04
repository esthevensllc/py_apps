from src.shared.batch.domain import ItemReader
import csv
import os

class PandasDataFrameReader(ItemReader):
    def __init__(self):
        self.chunk = 0
        self.chunk_counter = 0
        # self.dataframe = vaex.read_csv(self.context['filename'])
        self.context = None

    def start(self, context: dict):
        import pandas as pd

        self.context = context
        # self.dataframe = vaex.read_csv(f"{context['storage_dir']}/{context['filename']}")
        self.dataframe = pd.read_csv(f"{context['storage_dir']}/{context['filename']}")
        self.chunk = context['config']['chunk_limit']
        self.chunk_counter = 1
        self.context['file_count'] = len(self.dataframe)

    def read(self):
        chunk = self.chunk
        page = self.chunk_counter
        start_index = (page - 1) * chunk
        end_index = start_index + chunk
        # end_index = page * chunk
        df = self.dataframe.iloc[start_index:end_index]

        self.chunk_counter += 1
        return df.copy(deep=True) if len(df) > 0 else None


class DatabaseCursorReader(ItemReader):
    def __init__(self):
        self.chunk = 0
        self.chunk_counter = 0
        self.context = None
        self.on_next_callback = None

    def start(self, context: dict):
        self.context = context
        self.chunk = context['config']['chunk_limit']
        # self.chunk_counter = 0
        self.context['file_count'] = 0

    def read(self):
        cursor = self.context['poller']['cursor']
        rows = cursor.fetchmany(self.chunk)
        if rows is None:
            return None
        self.context['file_count'] += len(rows)
        return rows

    def on_next(self, callback):
        def callback_wrapper(rows):
            self.context['file_count'] += len(rows)
            return callback(rows)
        self.on_next_callback = callback_wrapper

    def subscribe(self):
        cursor = self.context['poller']['cursor']
        cursor.on_next(self.on_next_callback)
        cursor.subscribe()


class ReCsvReader(ItemReader):
    def __init__(self):
        self.chunk_limit = 0
        self.context = None
        self.on_next_callback = None

    def start(self, context: dict):
        self.context = context
        self.chunk_limit = context['config']['chunk_limit']
        self.context['file_count'] = 0

    def read(self):
        pass

    def on_next(self, callback):
        self.on_next_callback = callback

    def subscribe(self):
        with open(f"{self.context['storage_dir']}/{self.context['filename']}", newline='', encoding='UTF-8') as csvfile:
            file_delimiter = self.context['config'].get('file_delimiter', ',')
            skip_lines = self.context['config'].get('skip_lines', 1)
            reader = csv.reader(csvfile, delimiter=file_delimiter)
            for index in range(skip_lines):
                headers = list(next(reader))
                if self.context['poller'].get('columns') is None:
                    self.context['poller']['columns'] = headers
            
            chunk = []
            for row in reader:
                chunk.append(row)
                if len(chunk) == self.chunk_limit:
                    if self.context['poller'].get('columns') is None:
                        self.context['poller']['columns'] = [str(index) for index in range(len(chunk[0]))]
                    self.on_next_callback(chunk)
                    chunk = []
                    self.context['file_count'] += self.chunk_limit
            if len(chunk) >= 0:
                if len(chunk) > 0 and self.context['poller'].get('columns') is None:
                    self.context['poller']['columns'] = [str(index) for index in range(len(chunk[0]))]
                self.on_next_callback(chunk)
                self.context['file_count'] += len(chunk)
                chunk = []


class ReGzipReader(ItemReader):
    def __init__(self):
        self.chunk_limit = 0
        self.context = None
        self.on_next_callback = None

    def start(self, context: dict):
        self.context = context
        self.chunk_limit = context['config']['chunk_limit']
        self.context['file_count'] = 0

    def read(self):
        pass

    def on_next(self, callback):
        self.on_next_callback = callback

    def subscribe(self):
        import gzip
        from shutil import copyfileobj

        localfile = f"{context['storage_dir']}/{context['filename']}"
        unzip_localfile = f"{context['storage_dir']}/{context['filename']}".replace('.gz', '')

        with gzip.open(localfile, 'rb') as zf, open(unzip_localfile, 'wb') as subfile:
            copyfileobj(zf, subfile)
            files_by_parent[localfile] = [subfilename]
        os.unlink(localfile)
            
        csv_reader = ReCsvReader()
        csv_reader.start({
            'config': {'chunk_limit': self.chunk_limit},
            'storage_dir': context['storage_dir'],
            'filename': unzip_localfile,
        })
        csv_reader.on_next(self.on_next_callback)
        csv_reader.subscribe()

        self.context['file_count'] += csv_reader.chunk_limit

