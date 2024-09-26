import paramiko
import re
from src.shared.config import STORAGE_DIR
import os
import json
import datetime

class SFTPConnect:
    def __init__(self):
        self.connections = {
            'default': {'hostname': "172.19.145.55", 'username': "infoexp", 'password': "Cl@r0123", 'port': 22},
            'nce': {'hostname': "10.96.209.54", 'username': "ftpuser", 'password': "Changeme_123", 'port': 22},
            'nce02': {'hostname': "10.96.208.5", 'username': "ftpuser", 'password': "Changeme_123", 'port': 22},
            'nce03': {'hostname': "10.96.208.4", 'username': "ftpuser", 'password': "Changeme_123", 'port': 22},
            'nce04': {'hostname': "10.165.252.72", 'username': "ftpuser", 'password': "Changeme_123", 'port': 22},
            'nce05': {'hostname': "10.96.209.36", 'username': "ftpuser", 'password': "Changeme_123", 'port': 22},
            'nce06': {'hostname': "10.96.209.37", 'username': "ftpuser", 'password': "Changeme_123", 'port': 22},
            'xmlhuawei2_01': {'hostname': "10.96.210.9", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_02': {'hostname': "10.96.210.10", 'username': "calidad", 'password': "C4lid4d_123!", 'port': 22},
            'xmlhuawei2_03': {'hostname': "10.96.210.11", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_04': {'hostname': "10.96.210.12", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_05': {'hostname': "10.96.210.14", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_06': {'hostname': "10.96.210.15", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_07': {'hostname': "10.96.210.16", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_08': {'hostname': "10.96.210.17", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_09': {'hostname': "10.96.210.137", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_10': {'hostname': "10.96.210.138", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_11': {'hostname': "10.96.210.139", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_12': {'hostname': "10.96.210.140", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_13': {'hostname': "10.96.210.141", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_14': {'hostname': "10.96.210.142", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_15': {'hostname': "10.96.210.143", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_16': {'hostname': "10.96.210.144", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_17': {'hostname': "10.96.210.145", 'username': "calidad", 'password': "C4lid4d_123", 'port': 22},
            'xmlhuawei2_18': {'hostname': "172.31.19.135", 'username': "ossuser", 'password': "Changeme_123", 'port': 22},
            'portales': {'hostname': "172.17.27.157", 'username': "C16343", 'password': "oss700321", 'port': 22},
            'portales02': {'hostname': os.getenv("SFTP_PORTAL02_HOST"), 'username': os.getenv("SFTP_PORTAL02_USERNAME"), 'password': os.getenv("SFTP_PORTAL02_PASSWORD"), 'port': 22},
            'ana': {'hostname': "172.16.102.103", 'username': "C16343", 'password': "C16343", 'port': 22},
            'anadw': {'hostname': "172.16.102.103", 'username': "dwhouseuser", 'password': "DataWH$23", 'port': 22},
            'pronatel01': {'hostname': "172.31.17.20", 'username': "root", 'password': "Huawei12#$", 'port': 22},
            'pronatel02': {'hostname': "172.31.17.21", 'username': "root", 'password': "Huawei12#$", 'port': 22},
            'pronatel03': {'hostname': "172.31.17.22", 'username': "root", 'password': "Huawei12#$", 'port': 22},
            'pronatel04': {'hostname': "172.31.17.23", 'username': "root", 'password': "Huawei12#$", 'port': 22},
            'pronatel05': {'hostname': "172.19.255.48", 'username': "root", 'password': "Huawei12#$", 'port': 22},
            'pronatel06': {'hostname': "172.19.255.49", 'username': "root", 'password': "Huawei12#$", 'port': 22},
            'pronatel07': {'hostname': "172.19.255.50", 'username': "root", 'password': "Huawei12#$", 'port': 22},
            'pronatel08': {'hostname': "172.19.255.51", 'username': "root", 'password': "Huawei12#$", 'port': 22},
            'pronatel09': {'hostname': "172.19.255.88", 'username': "root", 'password': "Huawei12#$", 'port': 22},
            'zte': {'hostname': "10.95.241.170", 'username': "sftpDespred", 'password': "Cl4r0#23", 'port': 21128},
            'zte02': {'hostname': "10.95.241.170", 'username': "usrsdesemred", 'password': "DESred2#3$4", 'port': 21128},
        }
        self.connection = 'default'
        self.ssh_connections = {}
        self.transport_by_conn = {}
        self.max_cache_leaf = datetime.timedelta(minutes=10)

    def useConnection(self, connection):
        self.connection = connection
        self.connect()

    def connect(self):
        sftp = None
        if self.connection in self.ssh_connections.keys():
            sftp = self.ssh_connections[self.connection]
        else:
            config = self.connections[self.connection]
            transport = paramiko.Transport((config['hostname'], config['port']))
            transport.connect(None, config['username'], config['password'])

            sftp = paramiko.SFTPClient.from_transport(transport)


            #datos = dict(**self.connections[self.connection])
            #ssh_client = paramiko.SSHClient()
            #ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #ssh_client.connect(**datos)
            self.ssh_connections[self.connection] = sftp
            self.transport_by_conn[self.connection] = transport
        return sftp

    def disconnect(self):
        for index in self.ssh_connections.keys():
            self.ssh_connections[index].close()
            self.transport_by_conn[index].close()

    def getReference(self):
        return self.connect()

    def get_files(self, remote_dir, local_dir, str_fecha_to_filter, cache=False):
        sftp = self.getReference()
        try:
            sftp.chdir(remote_dir)
        except Exception as e:
            print(e)
            raise Exception(f"El directorio {remote_dir} no existe")
        
        """
        files = sftp.listdir(remote_dir)
        pattern = re.compile(str_fecha_to_filter)
        files_to_upload = []
        for fname in files:
            filename = fname
            if pattern.match(filename) is not None:
                path_filename = local_dir+filename
                try:
                    sftp.get(filename, path_filename)
                    files_to_upload.append({'updated': None, 'file': filename})
                    print(filename)
                except Exception as e:
                    raise Exception(f"Fallo al intentar copiar {filename} a {path_filename}. Tal vez es un directorio.")
        """
        
        files = self.get_filename_and_updated_at(remote_dir, str_fecha_to_filter, cache)
        files_to_upload = []
        for file in files:
            filename = file['file']
            path_filename = f"{local_dir}/{filename}"
            try:
                sftp.get(filename, path_filename)
                files_to_upload.append(file)
                #print(filename)
            except Exception as e:
                raise Exception(f"Fallo al intentar copiar {filename} a {path_filename}. Tal vez es un directorio.")

        return files_to_upload

    def get_filename_and_updated_at(self, work_dir, inicial_proyecto, cache=False):
        sftp = self.getReference()
        #files = sftp.listdir(work_dir)
        files = self.__listdir(work_dir, cache)
        pattern = re.compile(inicial_proyecto)
        files_to_upload = []
        for filename in files:
            if pattern.match(filename) is not None:
                stat_file = sftp.stat(f"{work_dir}/{filename}")
                mtime = datetime.datetime.fromtimestamp(stat_file.st_mtime)
                files_to_upload.append({
                    'updated': mtime.strftime('%Y-%m-%d %H:%M:%S'),
                    'file': filename,
                    'path': work_dir,
                    'st_mode': stat_file.st_mode
                })
        return files_to_upload

    def put(self, localfile, remotefile):
        self.getReference().put(localfile, remotefile)

    def __listdir(self, work_dir, cache):
        sftp = self.getReference()
        encode_wdir = work_dir.replace('/', '.')
        cache_file = f'{STORAGE_DIR}cache/sftp/ls_{encode_wdir}.txt'
        if cache == True:
            cache_is_valid = False
            if os.path.exists(cache_file):
                stat_file = os.stat(cache_file)
                mtime = datetime.datetime.fromtimestamp(stat_file.st_mtime)
                diff = datetime.datetime.now() - mtime
                if diff <= self.max_cache_leaf:
                    cache_is_valid = True
                    
            else:
                cache_is_valid = False
            
            if cache_is_valid:
                f = open(cache_file,'r')
                files = json.loads(f.read())
                f.close()
                self.__del_invalid_files()
                return files
            else:
                files = sftp.listdir(work_dir)
                f = open(cache_file,'w')
                f.write(json.dumps(files))
                f.close()
                self.__del_invalid_files()
                return files
        else:
            return sftp.listdir(work_dir)

    def __del_invalid_files(self):
        files = os.listdir(f'{STORAGE_DIR}cache/sftp')
        for f in files:
            if f in ('.gitkeep'):
                continue
            stat_file = os.stat(f'{STORAGE_DIR}cache/sftp/{f}')
            mtime = datetime.datetime.fromtimestamp(stat_file.st_mtime)
            diff = datetime.datetime.now() - mtime
            cache_is_valid = False
            if diff <= self.max_cache_leaf:
                cache_is_valid = True
            
            if not cache_is_valid:
                os.unlink(f'{STORAGE_DIR}cache/sftp/{f}')



            
    