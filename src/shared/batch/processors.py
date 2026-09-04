from src.shared.batch.domain import ItemProcessor

class ListProcessor(ItemProcessor):
    def __init__(self):
        self.context = dict()
        self.mapper_by_type = {
            "int": lambda value: self.map_int(value),
            "decimal": lambda value: float(value) if value is not None and value != '' else None,
            "number": lambda value: float(value) if value is not None and value != '' else None,
        }
    
    def start(self, context):
        self.context = context
        
    def process(self, items):
        headers = [field['src_fieldname'] for field in self.context['config']['fields']]
        headers_by_type = {}
        for field in self.context['config']['fields']:
            headers_by_type[field['src_fieldname']] = field['type']
        
        src_headers = self.get_items_columns()
        src_headers_index = {}
        for index in range(len(src_headers)):
            src_headers_index[src_headers[index]] = index

        # return [[row[src_headers_index[header]] for header in headers] for row in items]
        return [[self.map_value(row[src_headers_index[header]], headers_by_type[header]) for header in headers] for row in items]

    def get_items_columns(self):
        # return self.context['poller']['cursor'].get_columns()
        pass

    def map_value(self, value, type):
        return value if self.mapper_by_type.get(type, None) is None else self.mapper_by_type[type](value)
    
    def map_int(self, value):
        if value is not None:
            f = float(value)
            if f.is_integer():
                return int(f)
            else:
                raise ValueError(f"No es entero: {value}")
        return None
