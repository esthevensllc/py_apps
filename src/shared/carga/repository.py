class InMemoryConfigRepository:
    def __init__(self, db):
        self.db = db
        self.config_by_id = {}
    
    def get(self):
        result = []
        for id in list(self.config_by_id):
            row = dict(**self.config_by_id[id])
            if row.get("status") is not None:
                if row["status"] != 1:
                    continue
            row.pop("fields")
            result.append(row)
        return result

    def get_by_group_id(self, group_id):
        result = self.get()
        return list(filter(lambda r: r["m_group"] == group_id, result))

    def find(self, id):
        if id in self.config_by_id.keys():
            row = dict(**self.config_by_id[id])
            row.pop("fields")
            return row
        return None
    
    def get_fields_by_id(self, config_id):
        if config_id in self.config_by_id.keys():
            return self.config_by_id[config_id]["fields"]
        return []