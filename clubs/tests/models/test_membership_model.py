"""Unit tests for the Membership model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, Membership
from clubs.tests.helpers import CreateClubs


class MembershipModelTestCase(TestCase, CreateClubs):
    """Unit tests for the Membership model."""

    def setUp(self):
        self.club = self.create_one_club("John's Club", "Strand", "This is a club")

    def test_valid_membership(self):
        user = User.objects.get(username="hillaryunderside@example.org")
        membership =  Membership.objects.all().filter(user=user, club=self.club)[0]
        self._assert_membership_is_valid(membership)

    def test_user_must_be_part_of_membership_foreign_key(self):
        user = User.objects.get(username="hillaryunderside@example.org")
        membership = Membership.objects.all().filter(user=user, club=self.club)[0]
        membership.user = None
        self._assert_membership_is_invalid(membership)

    def test_club_must_be_part_of_membership_foreign_key(self):
        user = User.objects.get(username="hillaryunderside@example.org")
        membership = Membership.objects.all().filter(user=user, club=self.club)[0]
        membership.club = None
        self._assert_membership_is_invalid(membership)

    def test_level_may_be_between_zero_and_three(self):
        user = User.objects.get(username="hillaryunderside@example.org")
        membership = Membership.objects.all().filter(user=user, club=self.club)[0]
        membership.level = '0'
        self._assert_membership_is_valid(membership)
        membership.level = '1'
        self._assert_membership_is_valid(membership)
        membership.level = '2'
        self._assert_membership_is_valid(membership)
        membership.level = '3'
        self._assert_membership_is_valid(membership)

    def test_level_cannot_be_less_than_zero(self):
        user = User.objects.get(username="hillaryunderside@example.org")
        membership = Membership.objects.all().filter(user=user, club=self.club)[0]
        membership.level = '-1'
        self._assert_membership_is_invalid(membership)

    def test_level_cannot_be_more_than_three(self):
        user = User.objects.get(username="hillaryunderside@example.org")
        membership = Membership.objects.all().filter(user=user, club=self.club)[0]
        membership.level = '4'
        self._assert_membership_is_invalid(membership)

    def test_is_removed_user_correctly_returns_whether_the_user_has_been_removed(self):
        user = User.objects.get(username="hillaryunderside@example.org")
        membership = Membership.objects.all().filter(user=user, club=self.club)[0]
        self.assertFalse(membership.is_removed_user())
        membership.level = '0'
        self.assertTrue(membership.is_removed_user())

    def test_is_applicant_correctly_returns_whether_the_user_is_an_applicant(self):
        user = User.objects.get(username="hillaryunderside@example.org")
        membership = Membership.objects.all().filter(user=user, club=self.club)[0]
        self.assertFalse(membership.is_applicant())
        membership.level = '1'
        self.assertTrue(membership.is_applicant())

    def test_is_member_correctly_returns_whether_the_user_is_a_member(self):
        user = User.objects.get(username="pollyanatomato@example.org")
        membership = Membership.objects.all().filter(user=user, club=self.club)[0]
        self.assertFalse(membership.is_member())
        membership.level = '2'
        self.assertTrue(membership.is_member())

    def test_is_officer_correctly_returns_whether_the_user_is_an_officer(self):
        user = User.objects.get(username="hillaryunderside@example.org")
        membership = Membership.objects.all().filter(user=user, club=self.club)[0]
        self.assertFalse(membership.is_officer())
        membership.level = '3'
        self.assertTrue(membership.is_officer())

    def test_remove_user_correctly_removes_the_user(self):
        user = User.objects.get(username="hillaryunderside@example.org")
        membership = Membership.objects.all().filter(user=user, club=self.club)[0]
        membership.remove_user()
        self.assertEqual(membership.level, '0')

    def test_calling_remove_user_on_a_removed_user_leaves_them_still_removed(self):
        user = User.objects.get(username="hillaryunderside@example.org")
        membership = Membership.objects.all().filter(user=user, club=self.club)[0]
        membership.remove_user()
        self.assertEqual(membership.level, '0')
        membership.remove_user()
        self.assertEqual(membership.level, '0')

    def test_reinstate_user_correctly_reinstates_the_user(self):
        user = User.objects.get(username="hillaryunderside@example.org")
        membership = Membership.objects.all().filter(user=user, club=self.club)[0]
        membership.level = '0'
        membership.reinstate_user()
        self.assertEqual(membership.level, '1')

    def test_calling_reinstate_user_on_a_non_removed_user_does_not_change_their_level(self):
        user = User.objects.get(username="hillaryunderside@example.org")
        membership = Membership.objects.all().filter(user=user, club=self.club)[0]
        old_level = membership.level
        membership.reinstate_user()
        self.assertEqual(old_level, membership.level)

    def _assert_membership_is_valid(self, membership):
        try:
            membership.full_clean()
        except (ValidationError):
            self.fail("Test user should be valid")

    def _assert_membership_is_invalid(self, membership):
        with self.assertRaises(ValidationError):
            membership.full_clean()

    def create_one_officer(self):
        officer = self.create_user("tatianaubel", "Tatiana", "Ubel")
        return officer
    def create_one_member(self):
        member = self.create_user("rogeroldham", "Roger", "Oldham")
        return member
    def create_one_applicant(self):
        applicant = self.create_user("glenncloud", "Glenn", "Cloud")
        return applicant
