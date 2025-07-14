import pytest
import sys
import os

import unittest
from city_tour_loader import CityTourLoader
from memory_capsule.capsule import DigitalMemoryCapsule

class TestCityTourLoading(unittest.TestCase):
    def setUp(self):
        # Ordner mit Test-Dokumenten (am besten kleine Testdateien)
        self.test_folder = "tests/docs/paris"
        self.loader = CityTourLoader(self.test_folder)

    def test_load_all_overviews_returns_list(self):
        overviews = self.loader.load_all_overviews()
        self.assertIsInstance(overviews, list)
        self.assertGreater(len(overviews), 0, "Es sollten mindestens einige Dokumentübersichten geladen werden")

    def test_overviews_have_expected_keys(self):
        overviews = self.loader.load_all_overviews()
        for overview in overviews:
            self.assertIn("file_type", overview)
            self.assertIn("text_excerpt", overview)

    def test_create_memory_capsule(self):
        overviews = self.loader.load_all_overviews()
        capsule = DigitalMemoryCapsule(overviews)
        summary = capsule.summarize()
        self.assertIsInstance(summary, dict)
        self.assertIn("document_count", summary)
        self.assertEqual(summary["document_count"], len(overviews))

if __name__ == "__main__":
    unittest.main()
