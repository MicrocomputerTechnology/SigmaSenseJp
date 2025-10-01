import unittest
import os
import json
import shutil
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from src.sigmasense.config_loader import ConfigLoader

class TestConfigLoader(unittest.TestCase):

    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'temp_config_test')
        os.makedirs(self.test_dir, exist_ok=True)
        self.config_dir = os.path.join(self.test_dir, 'config')
        os.makedirs(self.config_dir, exist_ok=True)

        self.config1_path = os.path.join(self.config_dir, 'test_config1.json')
        self.config2_path = os.path.join(self.config_dir, 'test_config2.json')
        self.invalid_config_path = os.path.join(self.config_dir, 'invalid.json')
        self.non_json_path = os.path.join(self.config_dir, 'not_a_config.txt')

        with open(self.config1_path, 'w', encoding='utf-8') as f:
            json.dump({"key1": "value1", "num": 123}, f)

        with open(self.config2_path, 'w', encoding='utf-8') as f:
            json.dump({"key2": "value2", "bool": True}, f)

        with open(self.invalid_config_path, 'w', encoding='utf-8') as f:
            f.write("this is not json")

        with open(self.non_json_path, 'w', encoding='utf-8') as f:
            f.write("just some text")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_load_all_configs_success(self):
        loader = ConfigLoader(self.config_dir)
        configs = loader.get_all_configs()

        self.assertIn('test_config1', configs)
        self.assertIn('test_config2', configs)
        self.assertEqual(configs['test_config1']['key1'], 'value1')
        self.assertEqual(configs['test_config2']['bool'], True)
        self.assertNotIn('invalid', configs) # Invalid JSON should be skipped
        self.assertNotIn('not_a_config', configs) # Non-JSON should be skipped

    def test_get_config_by_name(self):
        loader = ConfigLoader(self.config_dir)
        config1 = loader.get_config('test_config1')
        config2 = loader.get_config('test_config2')
        non_existent = loader.get_config('non_existent_config')

        self.assertIsNotNone(config1)
        self.assertEqual(config1['key1'], 'value1')
        self.assertIsNotNone(config2)
        self.assertEqual(config2['bool'], True)
        self.assertIsNone(non_existent)

    def test_empty_config_directory(self):
        shutil.rmtree(self.config_dir)
        os.makedirs(self.config_dir)
        loader = ConfigLoader(self.config_dir)
        configs = loader.get_all_configs()
        self.assertEqual(len(configs), 0)

    def test_non_existent_config_directory(self):
        shutil.rmtree(self.test_dir)
        loader = ConfigLoader(self.config_dir)
        configs = loader.get_all_configs()
        self.assertEqual(len(configs), 0)

if __name__ == '__main__':
    unittest.main()
