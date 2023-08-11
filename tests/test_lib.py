import unittest
from txt2ics import make_calendar

class BasicTestCase(unittest.TestCase):

    def test_make_calendar(self):
        with open(file="../tests/todo.md", mode="r", encoding="utf-8") as todofile:
            cal = make_calendar(todofile)
            with open("../tests/todo.ics", 'rb') as icsfile:
                assert cal.to_ical() == icsfile.read()

if __name__ == '__main__':
    unittest.main()