import unittest


class ExampleTest(unittest.IsolatedAsyncioTestCase):
    def test_example(self) -> None:
        self.assertEqual(1, 2 - 1)
