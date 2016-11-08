import unittest
from app import parse_date, date_difference_in_seconds

class TestApp(unittest.TestCase):
	def test_date_parse(self):
		date = parse_date('2016-10-29T20:41:24.000-0700')

		self.assertEqual(date.year, 2016)
		self.assertEqual(date.month, 10)
		self.assertEqual(date.day, 29)
		self.assertEqual(date.hour, 20)
		self.assertEqual(date.minute, 41)
		self.assertEqual(date.second, 24)

		utc_offset_hours = date.utcoffset().total_seconds() / 60 / 60

		self.assertEqual(utc_offset_hours, -7)

	def test_date_difference_in_seconds(self):
		date_review = parse_date('2016-10-28T15:17:23.000-0700')
		date_closed = parse_date('2016-10-29T15:19:24.000-0700')

		self.assertEqual(121, date_difference_in_seconds(date_closed, date_review))

if __name__ == '__main__':
    unittest.main()