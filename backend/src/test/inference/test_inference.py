import unittest
import requests
import json
from src.config import SERVER_URL

class TestInferenceRoute(unittest.TestCase):
    def setUp(self):
        self.base_url = SERVER_URL
        self.test_cases = [
            {
                "input": "I want to play hockey for 2 hours in the morning",
                "expected_activity": "play hockey",
                "expected_duration": "2",
                "expected_unit": "hours",
                "expected_period": "morning"
            },
            {
                "input": "Read a book for 30 minutes in the evening",
                "expected_activity": "read book",
                "expected_duration": "30",
                "expected_unit": "minutes",
                "expected_period": "evening"
            },
            {
                "input": "Study math for three hours",
                "expected_activity": "study math",
                "expected_duration": "three",
                "expected_unit": "hours",
                "expected_period": ""
            }
        ]

    def test_inference_endpoint(self):
        """Test the /infer endpoint with various inputs"""
        for test_case in self.test_cases:
            with self.subTest(input_text=test_case["input"]):
                response = requests.post(
                    f"{self.base_url}/infer",
                    json={"text": test_case["input"]},
                    headers={"Content-Type": "application/json"}
                )

                self.assertEqual(response.status_code, 200)
                data = response.json()

                # Check if we got both parsed_info and raw_inference
                self.assertIn("parsed_info", data)
                self.assertIn("raw_inference", data)

                parsed_info = data["parsed_info"]

                # Check if all expected fields are present
                self.assertIn("task_name", parsed_info)
                self.assertIn("duration", parsed_info)
                self.assertIn("duration_unit", parsed_info)
                self.assertIn("time_of_day", parsed_info)

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        # Test missing text field
        response = requests.post(
            f"{self.base_url}/infer",
            json={},
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

        # Test invalid JSON
        response = requests.post(
            f"{self.base_url}/infer",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 400)

    def test_natural_language_variations(self):
        """Test different variations of natural language inputs"""
        variations = [
            "I need to study for 2 hours",
            "Want to exercise for 45 minutes in the evening",
            "Going to read books for one hour in the morning",
            "Practice piano for thirty minutes",
            "Code for 3 hours in the afternoon"
        ]

        for text in variations:
            with self.subTest(input_text=text):
                response = requests.post(
                    f"{self.base_url}/infer",
                    json={"text": text},
                    headers={"Content-Type": "application/json"}
                )

                self.assertEqual(response.status_code, 200)
                data = response.json()
                parsed_info = data["parsed_info"]

                # Verify that we got some meaningful extraction
                self.assertTrue(parsed_info["task_name"] or parsed_info["duration"])

    def test_raw_inference_structure(self):
        """Test the structure of raw inference output"""
        response = requests.post(
            f"{self.base_url}/infer",
            json={"text": "Study math for two hours in the morning"},
            headers={"Content-Type": "application/json"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        raw_inference = data["raw_inference"]

        # Check if raw inference contains all expected fields
        self.assertIn("state_sequence", raw_inference)
        self.assertIn("word_indices", raw_inference)
        self.assertIn("state_sequence_with_words", raw_inference)

        # Check if state sequence with words is properly formatted
        for state_word_pair in raw_inference["state_sequence_with_words"]:
            self.assertEqual(len(state_word_pair), 2)
            state, word = state_word_pair
            self.assertIsInstance(state, str)
            self.assertIsInstance(word, str)

def run_tests():
    unittest.main()

if __name__ == "__main__":
    run_tests() 