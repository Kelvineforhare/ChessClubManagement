"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User
from clubs.tests.helpers import CreateUsers


class UserModelTestCase(TestCase, CreateUsers):
    """Unit tests for the User model."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe@example.org')

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ""
        self._assert_user_is_invalid()

    def test_first_name_need_not_be_unique(self):
        second_user = User.objects.get(username='janedoe@example.org')
        self.user.first_name = second_user.first_name
        self._assert_user_is_valid()

    def test_first_name_may_contain_50_characters(self):
        self.user.first_name = "x" * 50
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_50_characters(self):
        self.user.first_name = "x" * 51
        self._assert_user_is_invalid()

    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ""
        self._assert_user_is_invalid()

    def test_last_name_need_not_be_unique(self):
        second_user = User.objects.get(username='janedoe@example.org')
        self.user.last_name = second_user.last_name
        self._assert_user_is_valid()

    def test_last_name_may_contain_50_characters(self):
        self.user.last_name = "x" * 50
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_50_characters(self):
        self.user.last_name = "x" * 51
        self._assert_user_is_invalid()

    def test_username_cannot_be_blank(self):
        self.user.username = ""
        self._assert_user_is_invalid()

    def test_username_must_be_unique(self):
        second_user = User.objects.get(username='janedoe@example.org')
        self.user.username = second_user.username
        self._assert_user_is_invalid()

    def test_username_may_contain_numbers(self):
        self.user.username = 'j0hndoe2@example.org'
        self._assert_user_is_valid()

    def test_username_must_contain_username_before_at_symbol(self):
        self.user.username = "@example.org"
        self._assert_user_is_invalid()

    def test_username_must_contain_at_symbol(self):
        self.user.username = "johndoe.example.org"
        self._assert_user_is_invalid()

        self.user.username = "johndoe@.org"
        self._assert_user_is_invalid()

    def test_username_must_contain_domain(self):
        self.user.username = "johndoe@example"
        self._assert_user_is_invalid()

    def test_username_must_not_contain_more_than_one_at(self):
        self.user.username = "johndoe@@example.org"
        self._assert_user_is_invalid()

    def test_bio_may_be_blank(self):
        self.user.bio = ""
        self._assert_user_is_valid()

    def test_bio_need_not_be_unique(self):
        second_user = User.objects.get(username='janedoe@example.org')
        self.user.bio = second_user.bio
        self._assert_user_is_valid()

    def test_bio_may_contain_520_characters(self):
        self.user.bio = "x" * 520
        self._assert_user_is_valid()

    def test_bio_must_not_contain_more_than_520_characters(self):
        self.user.bio = "x" * 521
        self._assert_user_is_invalid()

    def test_chess_level_may_be_between_1_and_5(self):
        self.user.chess_level = "3"
        self._assert_user_is_valid()

    def test_chess_level_cannot_be_above_5(self):
        self.user.chess_level = "6"
        self._assert_user_is_invalid()

    def test_chess_level_cannot_be_below_1(self):
        self.user.chess_level = "0"
        self._assert_user_is_invalid()

    def test_personal_statement_may_be_blank(self):
        self.user.personal_statement = ""
        self._assert_user_is_valid()

    def test_personal_statement_need_not_be_unique(self):
        second_user = User.objects.get(username='janedoe@example.org')
        self.user.personal_statement = second_user.personal_statement
        self._assert_user_is_valid()

    def test_personal_statement_may_contain_520_characters(self):
        self.user.personal_statement = "x" * 520
        self._assert_user_is_valid()

    def test_personal_statement_must_not_contain_more_than_520_characters(self):
        self.user.personal_statement = "x" * 521
        self._assert_user_is_invalid()

    def test_full_name_is_returned_correctly(self):
        self.assertEqual(self.user.full_name(), "John Doe")
        second_user = User.objects.get(username='janedoe@example.org')
        self.assertEqual(second_user.full_name(), "Jane Doe")

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail("Test user should be valid")

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()