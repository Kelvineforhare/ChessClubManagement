"""Tests of the accept applicant view"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import Membership, User
from clubs.tests.helpers import reverse_with_next, CreateClubs

class AcceptApplicantViewTestCase(TestCase, CreateClubs):
    """Tests of the accept applicant view"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = self.create_one_club("club1", "London", "A chess club")
        self.user = User.objects.get(username='jamesmoth@example.org')
        self.membership = Membership.objects.all().filter(user=self.user, club=self.club)[0]
        self.target_user = User.objects.get(username='pollyanatomato@example.org')
        self.target_membership = Membership.objects.all().filter(user=self.target_user, club=self.club)[0]
        self.owner = self.club.owner
        self.url = reverse('accept_club_applicant', kwargs={'user_id': self.target_user.id,'club_id':self.club.id})

    def test_accept_applicant_url(self):
        self.assertEqual(self.url,f'/accept_club_applicant/club_id_{self.club.id}/user_id_{self.target_user.id}')

    def test_accept_applicant_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_member_cannot_accept_an_applicant(self):
        self.membership.level = "2"
        self.membership.save()
        self.assertTrue(self.membership.is_member())
        self.assertTrue(self.target_membership.is_applicant())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('accept_club_applicant', kwargs={'user_id': self.target_user.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.membership.refresh_from_db()
        self.target_membership.refresh_from_db()
        response_url = reverse('profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTrue(self.membership.is_member())
        self.assertFalse(self.target_membership.is_member())
        self.assertTrue(self.target_membership.is_applicant())

    def test_officer_can_accept_an_applicant(self):
        self.assertTrue(self.membership.is_officer())
        self.assertTrue(self.target_membership.is_applicant())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('accept_club_applicant', kwargs={'user_id': self.target_user.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.membership.refresh_from_db()
        self.target_membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTrue(self.membership.is_officer())
        self.assertFalse(self.target_membership.is_applicant())
        self.assertTrue(self.target_membership.is_member())

    def test_officer_accept_applicant_with_invalid_id(self):
        self.assertTrue(self.membership.is_officer())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('accept_club_applicant', kwargs={'user_id': self.user.id+9999, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTrue(self.membership.is_officer())

    def test_owner_can_accept_an_applicant(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.assertTrue(self.target_membership.is_applicant())
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('accept_club_applicant', kwargs={'user_id': self.target_user.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.target_membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertFalse(self.target_membership.is_applicant())
        self.assertTrue(self.target_membership.is_member())

    def test_applicant_cannot_accept_themselves(self):
        self.assertTrue(self.target_membership.is_applicant())
        self.client.login(username=self.target_user.username, password='Password123')
        url = reverse('accept_club_applicant', kwargs={'user_id': self.target_user.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.target_membership.refresh_from_db()
        response_url = reverse('profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertFalse(self.target_membership.is_member())
        self.assertTrue(self.target_membership.is_applicant())

    def test_officer_cannot_accept_an_inactive_applicant(self):
        self.assertTrue(self.membership.is_officer())
        self.assertTrue(self.target_membership.is_applicant())
        self.target_user.is_active = False
        self.target_user.save()
        self.assertFalse(self.target_user.is_active)
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('accept_club_applicant', kwargs={'user_id': self.target_user.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.membership.refresh_from_db()
        self.target_membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTrue(self.membership.is_officer())
        self.assertFalse(self.target_membership.is_member())
        self.assertTrue(self.target_membership.is_applicant())

    def test_officer_cannot_accept_applicant_another_officer(self):
        self.assertTrue(self.membership.is_officer())
        self.target_membership.level= "3"
        self.target_membership.save()
        self.assertTrue(self.target_membership.is_officer())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('accept_club_applicant', kwargs={'user_id': self.target_user.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.membership.refresh_from_db()
        self.target_membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTrue(self.membership.is_officer())
        self.assertFalse(self.target_membership.is_member())
        self.assertTrue(self.target_membership.is_officer())

    def test_officer_cannot_accept_applicant_the_owner(self):
        self.assertTrue(self.membership.is_officer())
        self.assertTrue(self.club.is_owner(self.owner))
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('accept_club_applicant', kwargs={'user_id': self.owner.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.club.refresh_from_db()
        self.membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTrue(self.membership.is_officer())
        self.assertTrue(self.club.is_owner(self.owner))

    def test_officer_cannot_accept_themselves(self):
        self.assertTrue(self.membership.is_officer())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('accept_club_applicant', kwargs={'user_id': self.user.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertFalse(self.membership.is_member())
        self.assertTrue(self.membership.is_officer())

    def test_owner_cannot_accept_themselves(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('accept_club_applicant', kwargs={'user_id': self.owner.id, 'club_id':self.club.id})
        response = self.client.get(url, follow=True)
        self.club.refresh_from_db()
        response_url = reverse('user_list',kwargs={'club_id':self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertTrue(self.club.is_owner(self.owner))

    def test_owner_cannot_accept_applicant_an_officer(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.target_membership.level = "3"
        self.target_membership.save()
        self.assertTrue(self.target_membership.is_officer())
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('accept_club_applicant', kwargs={'user_id': self.target_user.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.target_membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertFalse(self.target_membership.is_member())
        self.assertTrue(self.target_membership.is_officer())

    def test_owner_cannot_accept_applicant_with_invalid_id(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('accept_club_applicant', kwargs={'user_id': self.owner.id+9999, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.target_membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_owner_cannot_accept_an_inactive_applicant(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.assertTrue(self.target_membership.is_applicant())
        self.target_user.is_active = False
        self.target_user.save()
        self.assertFalse(self.target_user.is_active)
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('accept_club_applicant', kwargs={'user_id': self.target_user.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.membership.refresh_from_db()
        self.target_membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertFalse(self.target_membership.is_member())
        self.assertTrue(self.target_membership.is_applicant())
