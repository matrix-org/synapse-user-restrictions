import aiounittest


class ExampleTest(aiounittest.AsyncTestCase):
    def test_example(self) -> None:
        self.assertEqual(1, 2 - 1)
