from src.shared.queue.RemoteConnectEventProducer import RemoteConnectEventProducer
from src.shared.queue.SimpleEventConsumer import EventConsumerFromConfig
from src.mmltask.shared.services import LOAD_MMLTASK_FROM_CONFIG
from src.shared.config import STORAGE_DIR
from src.shared.batch.domain import (ReactiveDataChunkStep, EventMapper, WorkingDirectoryCreator)
from src.shared.batch.pollers import SftpPoller
from src.shared.batch.readers import ItemReader
from src.shared.batch.processors import ListProcessor
from src.shared.batch.writers import OracleWriter

import os
import datetime as dt
import pandas as pd
from zipfile import ZipFile
import re
import json
from shutil import rmtree, copyfileobj
import gzip
from sshtunnel import SSHTunnelForwarder
import subprocess


class MmltaskConfigFinder:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, context):
        config = self.repo.find(context['config_id'])
        if config is not None:
            config['fields'] = self.repo.get_fields_by_id(context['config_id'])
        context['config'] = config
        return context


class MmltaskGzipReader(ItemReader):
    def __init__(self):
        self.chunk_limit = 0
        self.context = None
        self.on_next_callback = None
        self.base_shell_path = os.getenv('PYAPP_BASE_DIR')+'src/mmltask/shell'

    def start(self, context: dict):
        self.context = context
        self.chunk_limit = context['config']['chunk_limit']
        self.context['file_count'] = 0

    def read(self):
        pass

    def on_next(self, callback):
        self.on_next_callback = callback

    def subscribe(self):
        context = self.context
        localfile = f"{context['storage_dir']}/{context['filename']}"
        unzip_localfile = f"{context['storage_dir']}/{context['filename']}".replace('.gz', '.txt').replace(' ', '_')

        with gzip.open(localfile, 'rb') as zf, open(unzip_localfile, 'wb') as subfile:
            copyfileobj(zf, subfile)
        os.unlink(localfile)

        self._exec_command(f"sh {self.base_shell_path}/format_mmltask_file.sh {unzip_localfile} {context['storage_dir']}/temp")

        headers, data = [], []

        if self.context['config']['m_group'] == 'voltaje':
            headers, data = self._get_voltage_data(f"{context['storage_dir']}/temp")
        elif self.context['config']['m_group'] == 'temperatura':
            headers, data = self._get_temperature_data(f"{context['storage_dir']}/temp")
        elif self.context['config']['m_group'] == 'vswr':
            headers, data = self._get_vswr_data(f"{context['storage_dir']}/temp")

        self.context['reader'] = {'columns': headers}
        self.on_next_callback(data)
        self.context['file_count'] = len(data)

    def _exec_command(self, command):
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise Exception(result.stderr.decode('utf-8'))
        return result.stdout.decode('utf-8')

    def _get_voltage_data(self, storage_dir):
        v_files_nr1 = os.listdir(f'{storage_dir}/files/nr1')
        v_files_nr2 = os.listdir(f'{storage_dir}/files/nr2')
        v_files_nr3 = os.listdir(f'{storage_dir}/files/nr3')

        headers = ['result_time', 'ne_name', 'cabinet_no', 'subrack_no', 'slot_no', 'upeu_spare_power', 'bbu_spare_power', 'input_voltage']
        data = []

        for archivo in v_files_nr1:
            with open(f'{storage_dir}/files/nr1/{archivo}', 'r') as f:
                nr1_tp_content=f.read()
            
                nr1_ne_name = re.search(r'NE Name:\n\t(.*)', nr1_tp_content).group(1)
            
                nr1_mml_command_report = re.search(r'MML Command Report:\n\t(.*)', nr1_tp_content).group(1)
                nr1_result_time = re.search(r'\b(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\b', nr1_mml_command_report).group(1)
            
                nr1_cabinet_no = (re.search(r'Cabinet No.  =  (.*)', nr1_tp_content).group(1))
                nr1_subrack_no = (re.search(r'Subrack No.  =  (.*)', nr1_tp_content).group(1))
                nr1_slot_no = (re.search(r'Slot No.  =  (.*)', nr1_tp_content).group(1))
                nr1_upeu_spare_power = (re.search(r'UPEU Spare Power\(W\)  =  (.*)', nr1_tp_content).group(1))
                nr1_bbu_spare_power = (re.search(r'BBU Spare Power\(W\)  =  (.*)', nr1_tp_content).group(1))
                nr1_input_voltage = (re.search(r'Input Voltage\(0.1V\)  =  (.*)', nr1_tp_content).group(1))
            
                nr1_upeu_spare_power = None if nr1_upeu_spare_power == 'NULL' else nr1_upeu_spare_power
                nr1_bbu_spare_power = None if nr1_bbu_spare_power == 'NULL' else nr1_bbu_spare_power
                nr1_input_voltage = None if nr1_input_voltage == 'NULL' else nr1_input_voltage
            
                data.append([nr1_result_time,nr1_ne_name,nr1_cabinet_no,nr1_subrack_no,nr1_slot_no,nr1_upeu_spare_power,nr1_bbu_spare_power,nr1_input_voltage])

        for archivo in v_files_nr2:
            with open(f'{storage_dir}/files/nr2/{archivo}', 'r') as f:
                nr2_tp_content=f.read()
            
                nr2_ne_name = re.search(r'NE Name:\n\t(.*)', nr2_tp_content).group(1)
            
                nr2_mml_command_report = re.search(r'MML Command Report:\n\t(.*)', nr2_tp_content).group(1)
                nr2_result_time = re.search(r'\b(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\b', nr2_mml_command_report).group(1)
            
                nr2_upeu_status = re.findall(r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', nr2_tp_content)
                for results in nr2_upeu_status:
                    nr2_tp_data=[nr2_result_time,nr2_ne_name]
                    for rrN in results:
                        nr2_tp_data.append(None if rrN == 'NULL' else rrN)
                    data.append(nr2_tp_data)

        for archivo in v_files_nr3:
            with open(f'{storage_dir}/files/nr3/{archivo}', 'r') as f:
                nr3_tp_content=f.read()
                
                nr3_ne_name = re.search(r'NE Name:\n\t(.*)', nr3_tp_content).group(1)
                
                nr3_mml_command_report = re.search(r'MML Command Report:\n\t(.*)', nr3_tp_content).group(1)
                nr3_result_time = re.search(r'\b(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\b', nr3_mml_command_report).group(1)
                
                nr3_upeu_status = re.findall(r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', nr3_tp_content)
                
                for results in nr3_upeu_status:
                    nr3_tp_data=[nr3_result_time,nr3_ne_name]
                    for rrN in results:
                        nr3_tp_data.append(None if rrN == 'NULL' else rrN)
                    data.append(nr3_tp_data)

        return headers, data

    def _get_temperature_data(self, storage_dir):
        v_files_nr1 = os.listdir(f'{storage_dir}/files/nr1')
        v_files_nr2 = os.listdir(f'{storage_dir}/files/nr2')
        v_files_nr3 = os.listdir(f'{storage_dir}/files/nr3')

        headers = ['result_time', 'ne_name', 'cabinet_no', 'subrack_no', 'slot_no', 'board_temperature', 'hpa_temperature']
        v_data = []
          
        for archivo in v_files_nr1:
            with open(f'{storage_dir}/files/nr1/{archivo}', 'r') as f:
                nr1_tp_content=f.read()
                
                ne_name = re.search(r'NE Name:\n\t(.*)', nr1_tp_content).group(1)
                
                nr1_mml_command_report = re.search(r'MML Command Report:\n\t(.*)', nr1_tp_content).group(1)
                nr1_result_time = re.search(r'\b(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\b', nr1_mml_command_report).group(1)
                
                nr1_cabinet_no = (re.search(r'Cabinet No.  =  (.*)', nr1_tp_content).group(1))
                nr1_subrack_no = (re.search(r'Subrack No.  =  (.*)', nr1_tp_content).group(1))
                nr1_slot_no = (re.search(r'Slot No.  =  (.*)', nr1_tp_content).group(1))
                nr1_board_temperature_degree_celsius = (re.search(r'Board Temperature\(degree Celsius\)  =  (.*)', nr1_tp_content).group(1))
                nr1_hpa_temperature_degree_celsius = (re.search(r'HPA Temperature\(degree Celsius\)  =  (.*)', nr1_tp_content).group(1))
                #upeu_spare_power = (re.search(r'UPEU Spare Power\(W\)  =  (.*)', nr1_tp_content).group(1))
                #bbu_spare_power = (re.search(r'BBU Spare Power\(W\)  =  (.*)', nr1_tp_content).group(1))
                #input_voltage = (re.search(r'Input Voltage\(0.1V\)  =  (.*)', nr1_tp_content).group(1))
                
                nr1_board_temperature_degree_celsius = None if nr1_board_temperature_degree_celsius == 'NULL' else nr1_board_temperature_degree_celsius
                nr1_hpa_temperature_degree_celsius = None if nr1_hpa_temperature_degree_celsius == 'NULL' else nr1_hpa_temperature_degree_celsius
                
                v_data.append([nr1_result_time,ne_name,nr1_cabinet_no,nr1_subrack_no,nr1_slot_no,nr1_board_temperature_degree_celsius,nr1_hpa_temperature_degree_celsius])
          
        for archivo in v_files_nr2:
            with open(f'{storage_dir}/files/nr2/{archivo}', 'r') as f:
                nr2_tp_content=f.read()
                
                nr2_ne_name = re.search(r'NE Name:\n\t(.*)', nr2_tp_content).group(1)
                
                nr2_mml_command_report = re.search(r'MML Command Report:\n\t(.*)', nr2_tp_content).group(1)
                nr2_result_time = re.search(r'\b(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\b', nr2_mml_command_report).group(1)
                
                #upeu_status = re.findall(r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', nr2_tp_content)
                nr2_upeu_status = re.findall(r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\w+)', nr2_tp_content)
                for results in nr2_upeu_status:
                    nr2_tp_data=[nr2_result_time,nr2_ne_name]
                    for rrN in results:
                        nr2_tp_data.append(None if rrN == 'NULL' else rrN)
                    v_data.append(nr2_tp_data)
          
        for archivo in v_files_nr3:
            with open(f'{storage_dir}/files/nr3/{archivo}', 'r') as f:
                nr3_tp_content=f.read()
                
                nr3_ne_name = re.search(r'NE Name:\n\t(.*)', nr3_tp_content).group(1)
                
                nr3_mml_command_report = re.search(r'MML Command Report:\n\t(.*)', nr3_tp_content).group(1)
                nr3_result_time = re.search(r'\b(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\b', nr3_mml_command_report).group(1)
                nr3_upeu_status = re.findall(r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\w+)', nr3_tp_content)
                for results in nr3_upeu_status:
                    tp_data=[nr3_result_time,nr3_ne_name]
                    for rrN in results:
                        tp_data.append(None if rrN == 'NULL' else rrN)
                    v_data.append(tp_data)
          
        return headers, v_data
    
    def _get_vswr_data(self, storage_dir):
        v_files_nr1 = os.listdir(f'{storage_dir}/files/nr1')
        v_files_nr2 = os.listdir(f'{storage_dir}/files/nr2')
        v_files_nr3 = os.listdir(f'{storage_dir}/files/nr3')

        headers = ['result_time', 'ne_name', 'cabinet_no', 'subrack_no', 'slot_no', 'tx_channel_no', 'rf_port', 'vswr_value']
        data = []

        # print(f"nr1 list: {len(v_files_nr1)}")
        # print(f"nr2 list: {len(v_files_nr2)}")
        # print(f"nr3 list: {len(v_files_nr3)}")

        for archivo in v_files_nr1:
            with open(f'{storage_dir}/files/nr1/{archivo}', 'r') as f:
                nr1_tp_content=f.read()
            
                nr1_ne_name = re.search(r'NE Name:\n\t(.*)', nr1_tp_content).group(1)
            
                nr1_mml_command_report = re.search(r'MML Command Report:\n\t(.*)', nr1_tp_content).group(1)
                nr1_result_time = re.search(r'\b(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\b', nr1_mml_command_report).group(1)
            
                nr1_cabinet_no = (re.search(r'Cabinet No.  =  (.*)', nr1_tp_content).group(1))
                nr1_subrack_no = (re.search(r'Subrack No.  =  (.*)', nr1_tp_content).group(1))
                nr1_slot_no = (re.search(r'Slot No.  =  (.*)', nr1_tp_content).group(1))
                nr1_tx_channel_no = (re.search(r'TX Channel No.  =  (.*)', nr1_tp_content).group(1))
                nr1_rf_port = (re.search(r'RF Port  =  (.*)', nr1_tp_content).group(1))
                nr1_vswr_value = (re.search(r'VSWR\(0.01\)  =  (.*)', nr1_tp_content).group(1))
            
                nr1_tx_channel_no = None if nr1_tx_channel_no == 'NULL' else nr1_tx_channel_no
                nr1_rf_port = None if nr1_rf_port == 'NULL' else nr1_rf_port
                nr1_vswr_value = None if nr1_vswr_value == 'NULL' else nr1_vswr_value
            
                data.append([nr1_result_time,nr1_ne_name,nr1_cabinet_no,nr1_subrack_no,nr1_slot_no,nr1_tx_channel_no,nr1_rf_port,nr1_vswr_value])

        for archivo in v_files_nr2:
            with open(f'{storage_dir}/files/nr2/{archivo}', 'r') as f:
                nr2_tp_content=f.read()
            
                nr2_ne_name = re.search(r'NE Name:\n\t(.*)', nr2_tp_content).group(1)
            
                nr2_mml_command_report = re.search(r'MML Command Report:\n\t(.*)', nr2_tp_content).group(1)
                nr2_result_time = re.search(r'\b(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\b', nr2_mml_command_report).group(1)
            
                nr2_upeu_status = re.findall(r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+|NULL)\s+(\d+|NULL)', nr2_tp_content)
                for results in nr2_upeu_status:
                    nr2_tp_data=[nr2_result_time,nr2_ne_name]
                    for rrN in results:
                        nr2_tp_data.append(None if rrN == 'NULL' else rrN)
                    data.append(nr2_tp_data)

        for archivo in v_files_nr3:
            with open(f'{storage_dir}/files/nr3/{archivo}', 'r') as f:
                nr3_tp_content=f.read()
                
                nr3_ne_name = re.search(r'NE Name:\n\t(.*)', nr3_tp_content).group(1)
                
                nr3_mml_command_report = re.search(r'MML Command Report:\n\t(.*)', nr3_tp_content).group(1)
                nr3_result_time = re.search(r'\b(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\b', nr3_mml_command_report).group(1)
                
                nr3_upeu_status = re.findall(r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+|NULL)\s+(\d+|NULL)', nr3_tp_content)
                
                for results in nr3_upeu_status:
                    nr3_tp_data=[nr3_result_time,nr3_ne_name]
                    for rrN in results:
                        nr3_tp_data.append(None if rrN == 'NULL' else rrN)
                    data.append(nr3_tp_data)

        return headers, data


class MmltaskProcessor(ListProcessor):
    def start(self, context):
        super().start(context)
        headers_argument = list(filter(lambda row: row.get('reload_argument') is not None, self.context['config']['fields']))
        self.headers_argument = {}
        for row in headers_argument:
            self.headers_argument[row['fieldname']] = row['reload_argument']

        self.columns = None
    
    def process(self, items):
        extra_values = [self.context['file_date'], self.context['filename'], self.headers_argument['servidor']]
        items = [row + extra_values for row in items]
        for index in range(len(items)):
            if items[index][0] is not None:
                items[index][0] = dt.datetime.strptime(items[index][0], '%Y-%m-%d %H:%M:%S')
        return super().process(items)

    def get_items_columns(self):
        if self.columns is None:
            self.columns = self.context['reader']['columns']+['fecha', 'archivo', 'servidor']
        return self.columns


class MmltaskReportFromConfig:
    def __init__(self, db, repo, sftp_service, control_repo):
        self.config_finder = MmltaskConfigFinder(repo)
        self.poller = SftpPoller(sftp_service)
        self.chunk_task = ReactiveDataChunkStep(MmltaskGzipReader(), MmltaskProcessor(), OracleWriter(db.getReference(), control_repo))
        self.event_mapper = EventMapper()
        self.wk_creator = WorkingDirectoryCreator()
        self.base_storage_dir = f"{STORAGE_DIR}mmltask"
        self.storage_dir = None

    def execute(self, context):
        try:
            context = self.config_finder.execute(context)
            self.start(context)
            self.poller.download(context)
            context = self.chunk_task.execute(context)
            self.complete()
        except BaseException as e:
            self.error(e)

    def start(self, context):
        self.storage_dir = self.wk_creator.create(self.base_storage_dir)
        context['storage_dir'] = self.storage_dir

    def complete(self):
        self.end_time = dt.datetime.now()
        if self.storage_dir is not None:
            rmtree(self.storage_dir)

    def error(self, error):
        self.complete()
        raise error

    def event_handler(self, event):
        event_mapped = self.event_mapper.execute(event)
        self.execute(event_mapped)


class MmltaskEventProducer(RemoteConnectEventProducer):
    def __init__(self, repository, pg_db, control_carga_repo, queue_service):
        super().__init__(pg_db, control_carga_repo, queue_service)
        self.repository = repository

    def get_cargas_config(self, group_id=None):
        if group_id is not None:
            return self.repository.get_by_group_id(group_id)
        return self.repository.get()


class MmltaskEventConsumer(EventConsumerFromConfig):
    def __init__(self, queue_service, app_container, notification_service, repository):
        super().__init__(queue_service, app_container, notification_service, repository)
        self.handler_name = LOAD_MMLTASK_FROM_CONFIG
