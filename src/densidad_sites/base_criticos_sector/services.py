import datetime as dt

class LoadBaseCriticosSector:
    def __init__(self, source_repo, repository):
        self.source_repo = source_repo
        self.repository = repository

    def execute(self):
        date = dt.datetime.now() - dt.timedelta(days=7)
        semana_input = self.source_repo.get_semana_from_date(date)
        print(semana_input)
        self.source_repo.reload_sectores_4g_sem(date)
        sectores = self.source_repo.get_sectores_4g_sem()

        self.repository.insert_sectores_4g_sem(semana_input["anio"], semana_input["semana"], sectores)
        self.repository.reload_base_criticos_sector(semana_input["anio"], semana_input["semana"])