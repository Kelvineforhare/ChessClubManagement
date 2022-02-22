"""Tests of the show club view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Membership
from clubs.tests.helpers import CreateClubs, reverse_with_next
from with_asserts.mixin import AssertHTMLMixin

class ShowClubViewTestCase(TestCase, CreateClubs, AssertHTMLMixin):
    """Tests of the show club view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = self.create_one_club("Super Club", "London", "A chess club")
        self.url = reverse('show_club', kwargs={'club_id' : self.club.id})
        self.owner = self.club.owner
        self.user = User.objects.get(username='jamesmoth@example.org')
        self.membership = Membership.objects.all().filter(user=self.user, club=self.club)[0]

    def test_show_club_url(self):
        self.assertEqual(self.url,f'/show_club/club_id_{self.club.id}')

    def test_get_show_club_does_not_redirect_when_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_get_show_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_club.html')
        self.assertContains(response, self.club.name)
        self.assertContains(response, self.club.location)
        self.assertContains(response, self.club.description)
        self.assertContains(response, self.owner.username)
        self.assertContains(response, self.owner.full_name())
        self.assertContains(response, "Owner")

    def test_applicant_show_club_with_invalid_id(self):
        self.membership.level = "1"
        self.membership.save()
        self.assertTrue(self.membership.is_applicant())
        url = reverse('show_club', kwargs={'club_id' : self.club.id+9999})
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(url, follow=True)
        response_url = reverse('show_club', kwargs={'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_member_show_club_with_invalid_id(self):
        self.membership.level = "2"
        self.membership.save()
        self.assertTrue(self.membership.is_member())
        url = reverse('show_club', kwargs={'club_id' : self.club.id+9999})
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_officer_show_club_with_invalid_id(self):
        self.assertTrue(self.membership.is_officer())
        url = reverse('show_club', kwargs={'club_id' : self.club.id+9999})
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_owner_show_club_with_invalid_id(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('show_club', kwargs={'club_id': self.club.id+9999})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
