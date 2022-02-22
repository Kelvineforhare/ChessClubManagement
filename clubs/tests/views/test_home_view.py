"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import Membership, User
from clubs.tests.helpers import CreateClubs

class HomeViewTestCase(TestCase, CreateClubs):
    """Tests for the home view"""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('home')
        self.club = self.create_one_club("club1", "London", "A chess club")
        self.user = User.objects.get(username='jamesmoth@example.org')
        self.membership = Membership.objects.all().filter(user=self.user, club=self.club)[0]

    def test_home_url(self):
        self.assertEqual(self.url, "/")

    def test_get_home(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_applicant_get_home_redirects_when_logged_in(self):
        self.membership.level = "1"
        self.membership.save()
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        response_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_member_get_home_redirects_when_logged_in(self):
        self.membership.level = "2"
        self.membership.save()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_officer_get_home_redirects_when_logged_in(self):
        self.membership.level = "3"
        self.membership.save()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_owner_get_home_redirects_when_logged_in(self):
        self.owner = self.club.owner
        self.client.login(username=self.owner.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
