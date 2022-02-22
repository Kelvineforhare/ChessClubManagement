"""Tests of the demote officer view"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import Membership, User
from clubs.tests.helpers import CreateClubs, reverse_with_next

class DemoteOfficerViewTestCase(TestCase, CreateClubs):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = self.create_one_club("club1", "London", "A chess club")
        self.user = User.objects.get(username='hillaryunderside@example.org')
        self.membership = Membership.objects.all().filter(user=self.user, club=self.club)[0]
        self.target_user = User.objects.get(username='jamesmoth@example.org')
        self.target_membership = Membership.objects.all().filter(user=self.target_user, club=self.club)[0]
        self.owner = self.club.owner
        self.url = reverse('demote_club_officer', kwargs={'user_id': self.target_user.id,'club_id':self.club.id})

    def test_demote_member_url(self):
        self.assertEqual(self.url,f'/demote_club_officer/club_id_{self.club.id}/user_id_{self.target_user.id}')

    def test_demote_member_redirects_when_not_logged_in(self):
        url = reverse('demote_club_officer', kwargs={'user_id': self.target_user.id,'club_id':self.club.id})
        redirect_url = reverse_with_next('log_in', url)
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_owner_can_demote_officer_to_member(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.assertTrue(self.target_membership.is_officer())
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('demote_club_officer', kwargs={'user_id': self.target_user.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.target_membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertFalse(self.target_membership.is_officer())
        self.assertTrue(self.target_membership.is_member())

    def test_owner_cannot_demote_officer_with_invalid_id(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('demote_club_officer', kwargs={'user_id': self.target_user.id+9999, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.target_membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)


    def test_owner_cannot_demote_themselves(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('demote_club_officer', kwargs={'user_id': self.owner.id, 'club_id':self.club.id})
        response = self.client.get(url, follow=True)
        self.club.refresh_from_db()
        response_url = reverse('user_list',kwargs={'club_id':self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertTrue(self.club.is_owner(self.owner))


    def test_owner_cannot_demote_an_inactive_officer_to_member(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.assertTrue(self.target_membership.is_officer())
        self.target_user.is_active = False
        self.target_user.save()
        self.assertFalse(self.target_user.is_active)
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('demote_club_officer', kwargs={'user_id': self.target_user.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.membership.refresh_from_db()
        self.target_membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertFalse(self.target_membership.is_member())
        self.assertTrue(self.target_membership.is_officer())

    def test_applicant_cannot_demote_a_officer_to_member(self):
        self.membership.level = "1"
        self.membership.save()
        self.assertTrue(self.membership.is_applicant())
        self.assertTrue(self.target_membership.is_officer())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('demote_club_officer', kwargs={'user_id': self.target_user.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.membership.refresh_from_db()
        self.target_membership.refresh_from_db()
        response_url = reverse('profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTrue(self.membership.is_applicant())
        self.assertFalse(self.target_membership.is_member())
        self.assertTrue(self.target_membership.is_officer())

    def test_member_cannot_demote_an_officer_to_member(self):
        self.membership.level = "2"
        self.membership.save()
        self.assertTrue(self.membership.is_member())
        self.assertTrue(self.target_membership.is_officer())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('demote_club_officer', kwargs={'user_id': self.target_user.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.membership.refresh_from_db()
        self.target_membership.refresh_from_db()
        response_url = reverse('profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTrue(self.membership.is_member())
        self.assertFalse(self.target_membership.is_member())
        self.assertTrue(self.target_membership.is_officer())

    def test_officer_cannot_demote_themselves(self):
        self.membership.level = "3"
        self.membership.save()
        self.assertTrue(self.membership.is_officer())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('demote_club_officer', kwargs={'user_id': self.user.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.membership.refresh_from_db()
        self.target_membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTrue(self.membership.is_officer())
