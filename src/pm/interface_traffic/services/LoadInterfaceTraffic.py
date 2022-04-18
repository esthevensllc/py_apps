import datetime

class LoadInterfaceTraffic:
    def __init__(self, repository, pm_api):
        self.repository = repository
        self.pm_api = pm_api

    def execute(self, groups = ["Balanceadores","ROUTERS CACs","SEDES","CALL CENTERS"]):
        print(f"Carga pm.interface-traffic {groups}")
        for group in groups:
            params = {
                'resolution': 'HOUR',
                'period': '1d',
                'bh': 'Sun-Sat 10:00-17:00',
                '$format': 'json',
                '$expand': 'device,portmfs',
                '$select': 'device/ID,device/Name,portmfs/Resolution,portmfs/Timestamp,portmfs/im_BitsPerSecondIn,portmfs/im_BitsPerSecondOut,portmfs/im_UtilizationIn,portmfs/im_UtilizationOut',
                '$filter': f"((groups/Name eq '{group}'))"
            }
            resp = self.pm_api.get('odata/api/interfaces', options={'params': params})
            resp = resp.json()

            registros_to_insert = []
            min_date = None
            max_date = None
            for row in resp['d']['results']:
                for device_traffic in row['portmfs']['results']:
                    date = datetime.datetime.fromtimestamp(int(device_traffic['Timestamp']))
                    row_to_add = {
                        'device_id': row['device']['ID'],
                        'device_name': row['device']['Name'],
                        # 'group_name': group,
                        'portmfs_resolution': device_traffic['Resolution'],
                        'portmfs_timestamp': self.int_timestamp_to_strdate(device_traffic['Timestamp']),
                        'portmfs_im_UtilizationIn': device_traffic['im_UtilizationIn'],
                        'portmfs_im_BitsPerSecondIn': device_traffic['im_BitsPerSecondIn'],
                        'portmfs_im_UtilizationOut': device_traffic['im_UtilizationOut'],
                        'portmfs_im_BitsPerSecondOuT': device_traffic['im_BitsPerSecondOut']
                    }
                    if min_date is None:
                        min_date = date
                    elif date < min_date:
                        min_date = date
                    
                    if max_date is None:
                        max_date = date
                    elif date > max_date:
                        max_date = date

                    registros_to_insert.append(row_to_add)

            if min_date is not None and max_date is not None:
                print(f"max-min [{group}]: {min_date.strftime('%Y-%m-%d %H:%M:%S')} - {max_date.strftime('%Y-%m-%d %H:%M:%S')}")
                self.repository.delete_where_collectiontime_between(group, min_date, max_date)
            self.repository.insert_from_array(group, registros_to_insert)

            print(f"Registros [{group}]: {len(registros_to_insert)}")

    def int_timestamp_to_strdate(self, timestamp, to_format = '%Y-%m-%d %H:%M:%S'):
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime(to_format)

    def event_handler(self, event):
        if 'groups' in event['msg_body'].keys():
            if type(event['msg_body']['groups']) != type([]):
                raise Exception('El atributo groups deve ser un array')
        else:
            raise Exception('Error no se encontró el atributo groups')

        self.execute(event['msg_body']['groups'])
