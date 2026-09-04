import datetime as dt
import unittest

from src.nce_recarga.selector import NCEFileSelector


class NCEFileSelectorTest(unittest.TestCase):
    def setUp(self):
        self.selector = NCEFileSelector()
        self.start = dt.datetime(2026, 7, 12, 21, 0)
        self.end = dt.datetime(2026, 7, 13, 6, 0)

    def test_expected_group_count(self):
        groups = self.selector.expected_groups(self.start, self.end)
        self.assertEqual(1008, len(groups))

    def test_every_configured_family_matches_real_filename_shape(self):
        remote_dir = '/hfs_public/nbi/text/pfm_output/20260712/20260712'
        for family in self.selector.families:
            with self.subTest(family=family):
                item = self.selector.parse(
                    f'{family}_202607122100_01.csv',
                    remote_dir,
                )
                self.assertIsNotNone(item)
                self.assertEqual(family, item.family)

    def test_accepts_numeric_or_absent_suffix(self):
        remote_dir = '/hfs_public/nbi/text/pfm_output/20260712/20260712'
        with_suffix = self.selector.parse(
            'PM_IG1_5_202607122100_01.csv',
            remote_dir,
        )
        without_suffix = self.selector.parse(
            'PM_IG1_5_202607122105.csv',
            remote_dir,
        )

        self.assertIsNotNone(with_suffix)
        self.assertEqual('01', with_suffix.suffix)
        self.assertIsNotNone(without_suffix)
        self.assertIsNone(without_suffix.suffix)

    def test_rejects_unrequested_family_and_invalid_suffix(self):
        remote_dir = '/remote'
        self.assertIsNone(
            self.selector.parse(
                'PM_IG999_5_202607122100_01.csv',
                remote_dir,
            )
        )
        self.assertIsNone(
            self.selector.parse(
                'PM_IG1_5_202607122100_part.csv',
                remote_dir,
            )
        )

    def test_range_is_start_inclusive_and_end_exclusive(self):
        day12 = '/hfs_public/nbi/text/pfm_output/20260712/20260712'
        day13 = '/hfs_public/nbi/text/pfm_output/20260713/20260713'
        summary = self.selector.select(
            {
                day12: [
                    'PM_IG1_5_202607122055_01.csv',
                    'PM_IG1_5_202607122100_01.csv',
                ],
                day13: [
                    'PM_IG1_5_202607130555_01.csv',
                    'PM_IG1_5_202607130600_01.csv',
                ],
            },
            self.start,
            self.end,
        )

        self.assertEqual(
            [
                'PM_IG1_5_202607122100_01.csv',
                'PM_IG1_5_202607130555_01.csv',
            ],
            [item.filename for item in summary.items],
        )

    def test_multiple_files_for_same_timestamp_are_one_group(self):
        remote_dir = '/hfs_public/nbi/text/pfm_output/20260712/20260712'
        summary = self.selector.select(
            {
                remote_dir: [
                    'PM_IG1_5_202607122100_01.csv',
                    'PM_IG1_5_202607122100_02.csv',
                ]
            },
            self.start,
            self.end,
        )

        matching_groups = [
            group
            for group in summary.actual_groups
            if group == ('PM_IG1_5', self.start)
        ]
        self.assertEqual(2, len(summary.items))
        self.assertEqual(1, len(matching_groups))


if __name__ == '__main__':
    unittest.main()
