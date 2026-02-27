import unittest

from utils.validators import is_valid_email, validate_contact_form


class TestValidators(unittest.TestCase):
    def test_valid_contact_form(self):
        ok, message = validate_contact_form(
            "Pulindu",
            "pulindu@example.com",
            "This is a sufficiently long test message."
        )
        self.assertTrue(ok)
        self.assertEqual(message, "")

    def test_invalid_name(self):
        ok, message = validate_contact_form(
            "A",
            "pulindu@example.com",
            "This is a sufficiently long test message."
        )
        self.assertFalse(ok)
        self.assertIn("valid name", message)

    def test_invalid_email(self):
        self.assertFalse(is_valid_email("not-an-email"))
        self.assertFalse(is_valid_email("name@invalid"))
        self.assertTrue(is_valid_email("name@example.com"))

    def test_invalid_message(self):
        ok, message = validate_contact_form(
            "Pulindu",
            "pulindu@example.com",
            "short"
        )
        self.assertFalse(ok)
        self.assertIn("at least 10 characters", message)


if __name__ == "__main__":
    unittest.main()

