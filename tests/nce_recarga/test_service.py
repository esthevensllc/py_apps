import datetime as dt
import unittest

from src.nce_recarga.selector import NCEFileSelector
from src.nce_recarga.service import NCERecargaService, NCERecargaValidationError


class FakeSFTPService:
    def __init__(self, filenames_by_directory):
        self.filenames_by_directory = filenames_by_directory
        self.listed_directories = []

    def get_filenames(self, remote_dir, pattern):
        self.listed_directories.append((remote_dir, pattern))
        return self.filenames_by_directory[remote_dir]


class FakeLoadCSV:
    def __init__(self, sftp_service):
        self.sftp_service = sftp_service
        self.calls = []

    def execute(self, *args, **kwargs):
        self.calls.append((args, kwargs))


class NCERecargaServiceTest(unittest.TestCase):
    def setUp(self):
        self.start = dt.datetime(2026, 7, 12, 21, 0)
        self.end = dt.datetime(2026, 7, 12, 21, 10)
        self.remote_root = '/hfs_public/nbi/text/pfm_output'
        self.remote_dir = self.remote_root + '/20260712/20260712'
        self.selector = NCEFileSelector({'PM_IG1_5': 5})

    def build_service(self, filenames):
        sftp = FakeSFTPService({self.remote_dir: filenames})
        loader = FakeLoadCSV(sftp)
        service = NCERecargaService(
            load_csv=loader,
            remote_root=self.remote_root,
            selector=self.selector,
        )
        return service, sftp, loader

    def test_dry_run_lists_nested_daily_directory_without_loading(self):
        service, sftp, loader = self.build_service(
            [
                'PM_IG1_5_202607122100_01.csv',
                'PM_IG1_5_202607122105_01.csv',
            ]
        )

        result = service.execute(self.start, self.end, dry_run=True)

        self.assertEqual([(self.remote_dir, r'.*\.csv$')], sftp.listed_directories)
        self.assertEqual([], loader.calls)
        self.assertEqual(2, result['manifest_files'])
        self.assertEqual(0, result['missing_groups'])

    def test_execute_groups_suffixes_and_passes_exact_filenames(self):
        service, _, loader = self.build_service(
            [
                'PM_IG1_5_202607122100_01.csv',
                'PM_IG1_5_202607122100_02.csv',
                'PM_IG1_5_202607122105_01.csv',
            ]
        )

        result = service.execute(
            self.start,
            self.end,
            dry_run=False,
            emit_success_events=True,
        )

        self.assertEqual(2, len(loader.calls))
        first_args, first_kwargs = loader.calls[0]
        self.assertEqual('nce.pm_ig1_5_min', first_args[0])
        self.assertEqual(['PM_IG1_5'], first_args[1])
        self.assertEqual(self.start, first_args[2])
        self.assertEqual(self.remote_dir, first_kwargs['remote_dir'])
        self.assertEqual(
            [
                'PM_IG1_5_202607122100_01.csv',
                'PM_IG1_5_202607122100_02.csv',
            ],
            first_kwargs['filenames'],
        )
        self.assertTrue(first_kwargs['emit_success_event'])
        self.assertEqual(2, result['loaded_groups'])
        self.assertEqual(3, result['loaded_files'])

    def test_strict_mode_rejects_missing_group_before_loading(self):
        service, _, loader = self.build_service(
            ['PM_IG1_5_202607122100_01.csv']
        )

        with self.assertRaises(NCERecargaValidationError):
            service.execute(self.start, self.end, dry_run=False, strict=True)

        self.assertEqual([], loader.calls)


if __name__ == '__main__':
    unittest.main()
