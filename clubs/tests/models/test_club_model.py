"""Unit tests for the Club model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User
from clubs.tests.helpers import CreateClubs


class ClubModelTestCase(TestCase, CreateClubs):
    """Unit tests for the Club model."""

    def setUp(self):
        self.club = self.create_one_club("John's Club", "Strand", "This is a club")

    def test_valid_club(self):
        self._assert_club_is_valid()

    def test_club_name_must_not_be_blank(self):
        self.club.name = ""
        self._assert_club_is_invalid()

    def test_club_name_must_be_unique(self):
        second_club = self._create_second_club()
        self.club.name = second_club.name
        self._assert_club_is_invalid()

    def test_club_name_may_contain_50_characters(self):
        self.club.name = "x" * 50
        self._assert_club_is_valid()

    def test_club_name_must_not_contain_more_than_50_characters(self):
        self.club.name = "x" * 51
        self._assert_club_is_invalid()

    def test_club_location_must_not_be_blank(self):
        self.club.location = ""
        self._assert_club_is_invalid()

    def test_club_location_may_contain_50_characters(self):
        self.club.location = "x" * 50
        self._assert_club_is_valid()

    def test_club_location_must_not_contain_more_than_50_characters(self):
        self.club.location = "x" * 51
        self._assert_club_is_invalid()

    def test_club_description_must_not_be_blank(self):
        self.club.description = ""
        self._assert_club_is_invalid()

    def test_club_description_may_contain_50_characters(self):
        self.club.description = "x" * 50
        self._assert_club_is_valid()

    def test_club_description_must_not_contain_more_than_50_characters(self):
        self.club.description = "x" * 51
        self._assert_club_is_invalid()

    def test_club_has_an_owner(self):
        club = self._create_second_club()
        owner = User.objects.get(username="ramonaharper@example.org")
        self.assertEqual(club.owner, owner)

    def test_club_cannot_have_no_owner(self):
        self.club.owner = None
        self.club.save()
        self._assert_club_is_invalid()

    def test_is_part_of_with_a_member_of_the_club(self):
        user = User.objects.get(username="hillaryunderside@example.org")
        self.assertTrue(self.club.is_part_of(user))

    def test_is_part_of_with_the_owner_of_the_club(self):
        user = User.objects.get(username="johnsmith@example.org")
        self.assertTrue(self.club.is_part_of(user))

    def test_is_part_of_with_a_non_member_of_the_club(self):
        user = self.create_user("tatianaubel", "Tatiana", "Ubel")
        self.assertFalse(self.club.is_part_of(user))

    def test_is_owner_correctly_returns_whether_the_user_is_the_owner(self):
        user = User.objects.get(username="johnsmith@example.org")
        self.assertTrue(self.club.is_owner(user))
        user = self.create_user("tatianaubel", "Tatiana", "Ubel")
        self.assertFalse(self.club.is_owner(user))

    def test_string_function_correctly_returns_name_of_club(self):
        self.assertEqual(str(self.club), "John's Club")

    def _create_second_club(self):
        owner = self.create_user("ramonaharper@example.org", "Ramona", "Harper")
        officer = self.create_user("tatianaubel", "Tatiana", "Ubel")
        member = self.create_user("rogeroldham", "Roger", "Oldham")
        applicant = self.create_user("glenncloud", "Glenn", "Cloud")
        return self.create_club("Club 2", "Aldwych", "This is club 2", owner, officer, member, applicant)

    def _assert_club_is_valid(self):
        try:
            self.club.full_clean()
        except (ValidationError):
            self.fail("Test user should be valid")

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()
