class DepurarLogsPronatel:
    def __init__(self, sftp_service):
        self.sftp_service = sftp_service
        self.sftp_list = [
            {'id': 'pronatel01'},
            {'id': 'pronatel02'},
            {'id': 'pronatel03'},
            {'id': 'pronatel04'},
            {'id': 'pronatel05'},
            {'id': 'pronatel06'},
            {'id': 'pronatel07'},
            {'id': 'pronatel08'},
            {'id': 'pronatel09'},
        ]

    def execute(self):
        for server in self.sftp_list:
            self.sftp_service.useConnection(server['id'])
            sftp = self.sftp_service.getReference()
            try:
                attr = sftp.stat('/root/.local/share/lftp/transfer_log')
                # print(f"{server['id']}: {attr.st_size}")
                with sftp.file('/root/.local/share/lftp/transfer_log', 'w') as transfer_log:
                    print(f"{server['id']}: transfer_log actualizado")
            except FileNotFoundError:
                print(f"{server['id']}: El archivo transfer_log no existe")