import unittest, json, flask_unittest

import src.internalHandler as internalHandler

class TestExposeUser(unittest.TestCase):
    def setUp(self):
        my_app = internalHandler.app
        my_app.testing = True
        self.app = my_app.test_client()

    def test_home(self):
        result = self.app.get('/')
    
if __name__ == '__main__':
    unittest.main()