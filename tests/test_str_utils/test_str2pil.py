import base64
import os
import unittest

from PIL import Image

from zartist import str2pil


class TestStr2Pil(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a small test image
        cls.test_image = Image.new('RGB', (10, 10), color='red')
        cls.test_image_path = os.path.join(os.path.dirname(__file__), 'test_image.png')
        cls.test_image.save(cls.test_image_path)

        # Create base64 string
        with open(cls.test_image_path, 'rb') as img_file:
            img_data = img_file.read()
            cls.base64_image = f'data:image/png;base64,{base64.b64encode(img_data).decode()}'

    def test_local_file(self):
        img = str2pil(self.test_image_path)
        self.assertIsInstance(img, Image.Image)
        self.assertEqual(img.size, (10, 10))

    def test_base64(self):
        img = str2pil(self.base64_image)
        self.assertIsInstance(img, Image.Image)
        self.assertEqual(img.size, (10, 10))

    def test_invalid_path(self):
        with self.assertRaises(Exception):
            str2pil('nonexistent_image.png')

    def test_invalid_base64(self):
        with self.assertRaises(Exception):
            str2pil('data:image/png;base64,invalid_base64')

    def test_invalid_input(self):
        with self.assertRaises(Exception):
            str2pil('not_an_image_string')

    @classmethod
    def tearDownClass(cls):
        # Clean up test image
        if os.path.exists(cls.test_image_path):
            os.remove(cls.test_image_path)


if __name__ == "__main__":
    unittest.main()
