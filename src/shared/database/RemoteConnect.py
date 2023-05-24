import paramiko
import re

class RemoteConnect:
    def __init__(self):
        self.connections = {
            'default': {'hostname': "172.19.145.55", 'username': "infoexp", 'password': "Cl@r0123", 'port': 22},
            'limnwkvas01.tim.com.pe': {'hostname': "172.19.122.127", 'username': "USERVAS", 'password': "trafevades", 'port': 22},
        }
        self.connection = 'default'
        self.ssh_connections = {}

    def useConnection(self, connection):
        self.connection = connection
        self.connect()

    def connect(self) -> paramiko.SSHClient:
        ssh_client = None
        if self.connection in self.ssh_connections.keys():
            ssh_client = self.ssh_connections[self.connection]
        else:
            datos = dict(**self.connections[self.connection])
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(**datos)
            self.ssh_connections[self.connection] = ssh_client
        return ssh_client

    def disconnect(self):
        for index in self.ssh_connections.keys():
            self.ssh_connections[index].close()

    def getReference(self):
        return self.connect()

    def exec_command(self, command):
        ssh_client = self.connect()
        stdin,stdout,stderr = ssh_client.exec_command(command)
        status = stdout.channel.recv_exit_status()
        if status == 0:
            return stdout.readlines()
        else:
            print("".join(stderr.readlines()))
            return None

    def get_files(self, remote_dir, local_dir, str_fecha_to_filter):
        sftp = self.getReference().open_sftp()
        # remote_dir = '/opt/oss/server/var/neftpboot/ftproot/{}'.format(str_fecha_dir)
        try:
            sftp.chdir(remote_dir)
            archivos = self.get_filename_and_updated_at(remote_dir, str_fecha_to_filter)
        except Exception as e:
            raise e
            raise Exception("El directorio {} no existe".format(remote_dir))
        # archivos = sftp.listdir_attr('/opt/oss/server/var/neftpboot/ftproot/20220113')
        patron = re.compile(str_fecha_to_filter)
        files_to_upload = []
        for archivo in archivos:
            filename = archivo['file']
            if patron.match(filename) is not None:
                # if str_fecha_to_filter in filename and 'alarm-log-auto-1' in filename:
                try:
                    sftp.get(filename, local_dir+filename)
                    files_to_upload.append(archivo)
                    print(filename)
                except Exception as e:
                    print("Fallo al intentar copiar {} a {}. Tal vez es un directorio.".format(filename, local_dir+filename))
                    raise Exception("Fallo al intentar copiar {} a {}. Tal vez es un directorio.".format(filename, local_dir+filename))
        sftp.close()
        return files_to_upload

    def get_filename_and_updated_at(self, work_dir, inicial_proyecto):
        # --time-style=long-iso
        command = "ls \""+work_dir+"\" -lt --time-style=\"+%Y-%m-%d %H:%M:%S\" | grep \""+inicial_proyecto+"\" | awk '{print $6, $7, $8}'"
        # resp = self.remote_connect.exec_command(command)
        # "ls /opt/oss/server/var/neftpboot/ftproot -lt --time-style=long-iso | grep Board | awk '{print $6\"_\" $7, $8}'""ls /opt/oss/server/var/neftpboot/ftproot -lt --time-style=long-iso | grep Board | awk '{print $6\"_\" $7, $8}'"
        resp = self.exec_command(command)
        # print('len')
        # print(resp[0])
        archivos = []
        range_files = range(len(resp))
        for index in range_files:
            try:
                archivos.append({'updated': resp[index][0:19], 'file': resp[index][20:len(resp[index])].replace("\n", "")})
            except:
                print(resp[index])
        return archivos


