from src.shared.batch.domain import ItemReader
import pandas as pd

class PandasDataFrameReader(ItemReader):
    def __init__(self):
        self.chunk = 0
        self.chunk_counter = 0
        # self.dataframe = vaex.read_csv(self.context['filename'])
        self.context = None

    def start(self, context: dict):
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
        self.on_next_callback = callback

    def subscribe(self):
        cursor = self.context['poller']['cursor']
        cursor.on_next(self.on_next_callback)
        cursor.subscribe()

