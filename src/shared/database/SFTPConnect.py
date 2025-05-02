import paramiko
import re
from src.shared.config import STORAGE_DIR
import os
import json
import datetime
import shutil

class SFTPConnect:
    def __init__(self):
        self.connections = {
            'default': {'hostname': os.getenv("SFTP_HOST"), 'username': os.getenv("SFTP_USERNAME"), 'password': os.getenv("SFTP_PASSWORD"), 'port': int(os.getenv("SFTP_PORT", 22))},
            'nce': {'hostname': os.getenv("SFTP_NCE_HOST"), 'username': os.getenv("SFTP_NCE_USERNAME"), 'password': os.getenv("SFTP_NCE_PASSWORD"), 'port': int(os.getenv("SFTP_NCE_PORT", 22))},
            'nce02': {'hostname': os.getenv("SFTP_NCE02_HOST"), 'username': os.getenv("SFTP_NCE02_USERNAME"), 'password': os.getenv("SFTP_NCE02_PASSWORD"), 'port': int(os.getenv("SFTP_NCE02_PORT", 22))},
            'nce03': {'hostname': os.getenv("SFTP_NCE03_HOST"), 'username': os.getenv("SFTP_NCE03_USERNAME"), 'password': os.getenv("SFTP_NCE03_PASSWORD"), 'port': int(os.getenv("SFTP_NCE03_PORT", 22))},
            'nce04': {'hostname': os.getenv("SFTP_NCE04_HOST"), 'username': os.getenv("SFTP_NCE04_USERNAME"), 'password': os.getenv("SFTP_NCE04_PASSWORD"), 'port': int(os.getenv("SFTP_NCE04_PORT", 22))},
            'nce05': {'hostname': os.getenv("SFTP_NCE05_HOST"), 'username': os.getenv("SFTP_NCE05_USERNAME"), 'password': os.getenv("SFTP_NCE05_PASSWORD"), 'port': int(os.getenv("SFTP_NCE05_PORT", 22))},
            'nce06': {'hostname': os.getenv("SFTP_NCE06_HOST"), 'username': os.getenv("SFTP_NCE06_USERNAME"), 'password': os.getenv("SFTP_NCE06_PASSWORD"), 'port': int(os.getenv("SFTP_NCE06_PORT", 22))},
            'xmlhuawei2_01': {'hostname': os.getenv("SFTP_HUAWEI01_HOST"), 'username': os.getenv("SFTP_HUAWEI01_USERNAME"), 'password': os.getenv("SFTP_HUAWEI01_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI01_PORT", 22))},
            'xmlhuawei2_02': {'hostname': os.getenv("SFTP_HUAWEI02_HOST"), 'username': os.getenv("SFTP_HUAWEI02_USERNAME"), 'password': os.getenv("SFTP_HUAWEI02_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI02_PORT", 22))},
            'xmlhuawei2_03': {'hostname': os.getenv("SFTP_HUAWEI03_HOST"), 'username': os.getenv("SFTP_HUAWEI03_USERNAME"), 'password': os.getenv("SFTP_HUAWEI03_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI03_PORT", 22))},
            'xmlhuawei2_04': {'hostname': os.getenv("SFTP_HUAWEI04_HOST"), 'username': os.getenv("SFTP_HUAWEI04_USERNAME"), 'password': os.getenv("SFTP_HUAWEI04_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI04_PORT", 22))},
            'xmlhuawei2_05': {'hostname': os.getenv("SFTP_HUAWEI05_HOST"), 'username': os.getenv("SFTP_HUAWEI05_USERNAME"), 'password': os.getenv("SFTP_HUAWEI05_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI05_PORT", 22))},
            'xmlhuawei2_06': {'hostname': os.getenv("SFTP_HUAWEI06_HOST"), 'username': os.getenv("SFTP_HUAWEI06_USERNAME"), 'password': os.getenv("SFTP_HUAWEI06_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI06_PORT", 22))},
            'xmlhuawei2_07': {'hostname': os.getenv("SFTP_HUAWEI07_HOST"), 'username': os.getenv("SFTP_HUAWEI07_USERNAME"), 'password': os.getenv("SFTP_HUAWEI07_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI07_PORT", 22))},
            'xmlhuawei2_08': {'hostname': os.getenv("SFTP_HUAWEI08_HOST"), 'username': os.getenv("SFTP_HUAWEI08_USERNAME"), 'password': os.getenv("SFTP_HUAWEI08_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI08_PORT", 22))},
            'xmlhuawei2_09': {'hostname': os.getenv("SFTP_HUAWEI09_HOST"), 'username': os.getenv("SFTP_HUAWEI09_USERNAME"), 'password': os.getenv("SFTP_HUAWEI09_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI09_PORT", 22))},
            'xmlhuawei2_10': {'hostname': os.getenv("SFTP_HUAWEI10_HOST"), 'username': os.getenv("SFTP_HUAWEI10_USERNAME"), 'password': os.getenv("SFTP_HUAWEI10_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI10_PORT", 22))},
            'xmlhuawei2_11': {'hostname': os.getenv("SFTP_HUAWEI11_HOST"), 'username': os.getenv("SFTP_HUAWEI11_USERNAME"), 'password': os.getenv("SFTP_HUAWEI11_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI11_PORT", 22))},
            'xmlhuawei2_12': {'hostname': os.getenv("SFTP_HUAWEI12_HOST"), 'username': os.getenv("SFTP_HUAWEI12_USERNAME"), 'password': os.getenv("SFTP_HUAWEI12_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI12_PORT", 22))},
            'xmlhuawei2_13': {'hostname': os.getenv("SFTP_HUAWEI13_HOST"), 'username': os.getenv("SFTP_HUAWEI13_USERNAME"), 'password': os.getenv("SFTP_HUAWEI13_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI13_PORT", 22))},
            'xmlhuawei2_14': {'hostname': os.getenv("SFTP_HUAWEI14_HOST"), 'username': os.getenv("SFTP_HUAWEI14_USERNAME"), 'password': os.getenv("SFTP_HUAWEI14_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI14_PORT", 22))},
            'xmlhuawei2_15': {'hostname': os.getenv("SFTP_HUAWEI15_HOST"), 'username': os.getenv("SFTP_HUAWEI15_USERNAME"), 'password': os.getenv("SFTP_HUAWEI15_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI15_PORT", 22))},
            'xmlhuawei2_16': {'hostname': os.getenv("SFTP_HUAWEI16_HOST"), 'username': os.getenv("SFTP_HUAWEI16_USERNAME"), 'password': os.getenv("SFTP_HUAWEI16_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI16_PORT", 22))},
            'xmlhuawei2_17': {'hostname': os.getenv("SFTP_HUAWEI17_HOST"), 'username': os.getenv("SFTP_HUAWEI17_USERNAME"), 'password': os.getenv("SFTP_HUAWEI17_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI17_PORT", 22))},
            'xmlhuawei2_18': {'hostname': os.getenv("SFTP_HUAWEI18_HOST"), 'username': os.getenv("SFTP_HUAWEI18_USERNAME"), 'password': os.getenv("SFTP_HUAWEI18_PASSWORD"), 'port': int(os.getenv("SFTP_HUAWEI18_PORT", 22))},
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
            'zte': {'hostname': os.getenv("SFTP_ZTE_HOST"), 'username': os.getenv("SFTP_ZTE_USERNAME"), 'password': os.getenv("SFTP_ZTE_PASSWORD"), 'port': int(os.getenv("SFTP_ZTE_PORT"))},
            'zte02': {'hostname': os.getenv("SFTP_ZTE02_HOST"), 'username': os.getenv("SFTP_ZTE02_USERNAME"), 'password': os.getenv("SFTP_ZTE02_PASSWORD"), 'port': int(os.getenv("SFTP_ZTE02_PORT"))},
            'zte03': {'hostname': os.getenv("SFTP_ZTE03_HOST"), 'username': os.getenv("SFTP_ZTE03_USERNAME"), 'password': os.getenv("SFTP_ZTE03_PASSWORD"), 'port': int(os.getenv("SFTP_ZTE03_PORT"))},
            'limqredv02': {'hostname': os.getenv("SFTP_LIMQREDV02_HOST"), 'username': os.getenv("SFTP_LIMQREDV02_USERNAME"), 'password': os.getenv("SFTP_LIMQREDV02_PASSWORD"), 'port': int(os.getenv("SFTP_LIMQREDV02_PORT"))},
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
            sftp = None
            transport = None
            if config['hostname'] in ('127.0.0.1', 'localhost'):
                sftp = SftpLocal()
                transport = sftp
            else:
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


class SftpLocal:
    def __init__(self):
        self.path = ''

    def chdir(self, path):
        self.path = path

    def get(self, remotepath, localpath, callback=None, prefetch=True):
        if self.path == '':
            shutil.copy(remotepath, localpath)
        else:
            shutil.copy(f"{self.path}/{remotepath}", localpath)

    def stat(self, path):
        os.stat(path)

    def put(self, localpath, remotepath, callback=None, confirm=True):
        shutil.copy(localpath, remotepath)

    def listdir(self, path):
        return os.listdir(path)
    
    def close(self):
        pass

    

            
    