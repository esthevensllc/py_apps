import datetime as dt
import sys
import types
import unittest
from unittest.mock import Mock


config_module = types.ModuleType('src.shared.config')
config_module.STORAGE_DIR = '/tmp/'
config_module.BASE_DIR = '/app/'
config_module.DTFORMAT_BY_ALIAS = {
    'dxd': '%Y-%m-%d',
    'hxh': '%Y-%m-%d %H',
    'mxm': '%Y-%m-%d %H:%M',
}
sys.modules.setdefault('src.shared', types.ModuleType('src.shared'))
sys.modules['src.shared.config'] = config_module

cx_oracle_module = types.ModuleType('cx_Oracle')
cx_oracle_module.NUMBER = object()
cx_oracle_module.STRING = object()
sys.modules['cx_Oracle'] = cx_oracle_module

apic_module = types.ModuleType('src.apic')
apic_module.__path__ = []
apic_shared_module = types.ModuleType('src.apic.shared')
apic_shared_module.__path__ = []
apic_services_module = types.ModuleType('src.apic.shared.services')
apic_services_module.BaseApicService = object
sys.modules.setdefault('src.apic', apic_module)
sys.modules.setdefault('src.apic.shared', apic_shared_module)
sys.modules['src.apic.shared.services'] = apic_services_module

from src.nce.cargas.services.LoadCSV import LoadCSV


class FakeSFTPReference:
    def __init__(self):
        self.chdir_calls = []
        self.stat_calls = []
        self.get_calls = []

    def chdir(self, remote_dir):
        self.chdir_calls.append(remote_dir)

    def stat(self, remote_path):
        self.stat_calls.append(remote_path)
        return types.SimpleNamespace(st_mtime=0)

    def get(self, filename, local_path, prefetch=False):
        self.get_calls.append((filename, local_path, prefetch))


class FakeSFTPService:
    def __init__(self):
        self.reference = FakeSFTPReference()
        self.get_filenames = Mock(side_effect=AssertionError('No debe listar de nuevo'))

    def getReference(self):
        return self.reference


class LoadCSVExtensionTest(unittest.TestCase):
    def build_loader(self):
        return LoadCSV(None, None, None, FakeSFTPService())

    def test_exact_filenames_are_validated_and_downloaded_without_relisting(self):
        loader = self.build_loader()
        filename = 'PM_IG1_5_202607122100_01.csv'

        files = loader.get_files(
            '/remote/20260712/20260712',
            '/local',
            r'^PM_IG1_5_202607122100(?:_[0-9]+)?\.csv$',
            filenames=[filename],
        )

        self.assertEqual(filename, files[0]['file'])
        self.assertEqual(
            ['/remote/20260712/20260712/' + filename],
            loader.sftp_service.reference.stat_calls,
        )
        self.assertEqual(
            [(filename, '/local/' + filename, False)],
            loader.sftp_service.reference.get_calls,
        )

    def test_event_subdir_builds_nested_remote_path(self):
        loader = self.build_loader()
        loader.execute = Mock()
        event = {
            'queue_id': 'nce.pm_ig1_5_min',
            'msg_body': {
                'mediciones': ['PM_IG1_5'],
                'fec_ini': '2026-07-12 21:00',
                'format': 'mxm',
                'subdir': '20260712',
            },
        }

        loader.event_handler(event)

        loader.execute.assert_called_once_with(
            'nce.pm_ig1_5_min',
            ['PM_IG1_5'],
            dt.datetime(2026, 7, 12, 21, 0),
            'mxm',
            remote_dir=(
                '/hfs_public/nbi/text/pfm_output/20260712/20260712'
            ),
        )

    def test_event_rejects_unsafe_subdir(self):
        loader = self.build_loader()
        event = {
            'queue_id': 'nce.pm_ig1_5_min',
            'msg_body': {
                'mediciones': ['PM_IG1_5'],
                'fec_ini': '2026-07-12 21:00',
                'format': 'mxm',
                'subdir': '../20260712',
            },
        }

        with self.assertRaisesRegex(Exception, 'YYYYMMDD'):
            loader.event_handler(event)


if __name__ == '__main__':
    unittest.main()
