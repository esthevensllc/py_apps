from src.nce.cargas.services.BaseGenericEventProducer import BaseGenericEventProducer

class CargasEventProducer:
    def __init__(self, repository, generic_event_producer):
        self.repository = repository
        self.generic_event_producer = generic_event_producer
        self.filter_med = ['PM_IG27']

    def execute(self):
        mediciones_config = self.repository.get()
        #mediciones_config = list(filter(lambda row: row['codigo_medicion'] in self.filter_med, mediciones_config))
        for row in mediciones_config:
            medicion_granularidad = f"{row['codigo_medicion']}_{row['granularidad']}"
            self.generic_event_producer.set_config(
                f'nce.{medicion_granularidad}_min'.lower(),
                f'nce.{medicion_granularidad}_min'.lower(),
                medicion_granularidad
            )
            self.generic_event_producer.execute()

