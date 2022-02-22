"""Tests of the owner transfer view"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import Membership, User
from clubs.tests.helpers import CreateClubs, reverse_with_next

class OwnerTransferViewTestCase(TestCase, CreateClubs):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = self.create_one_club("John's Club", "Strand", "This is a club")
        self.user = User.objects.get(username='johnsmith@example.org')
        self.target_user = User.objects.get(username='jamesmoth@example.org')
        self.membership = Membership.objects.all().filter(user=self.target_user.id, club=self.club)[0]
        self.url = reverse('owner_transfer', kwargs={'user_id': self.target_user.id,'club_id':self.club.id})

    def test_owner_transfer_url(self):
        self.assertEqual(self.url,f'/owner_transfer/club_id_{self.club.id}/user_id_{self.target_user.id}')

    def test_owner_transfer_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_owner_can_transfer_ownership_to_officer(self):
        self.assertTrue(self.club.is_owner(self.user))
        self.assertTrue(self.membership.is_officer())
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.club.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id':self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertFalse(self.club.is_owner(self.user))
        old_owner_membership = Membership.objects.all().filter(user=self.user.id, club=self.club)[0]
        self.assertTrue(old_owner_membership.is_officer())
        self.assertEqual(len(Membership.objects.all().filter(user=self.target_user.id, club=self.club)), 0)
        self.assertTrue(self.membership.is_officer())
        self.assertTrue(self.club.is_owner(self.target_user))

    def test_owner_transfer_ownership_with_invalid_id(self):
        self.assertTrue(self.club.is_owner(self.user))
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('owner_transfer', kwargs={'user_id': self.user.id+9999,'club_id':self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list',kwargs={'club_id':self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertTrue(self.club.is_owner(self.user))

    def test_owner_cannot_transfer_ownership_to_themselves(self):
        self.assertTrue(self.club.is_owner(self.user))
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('owner_transfer', kwargs={'user_id': self.user.id,'club_id':self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list',kwargs={'club_id':self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertTrue(self.club.is_owner(self.user))

    def test_owner_cannot_transfer_ownership_to_applicant(self):
        self.assertTrue(self.club.is_owner(self.user))
        applicant = User.objects.get(username = "pollyanatomato@example.org")
        applicant_membership = Membership.objects.all().filter(user=applicant.id, club=self.club)[0]
        self.assertTrue(applicant_membership.is_applicant())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('owner_transfer', kwargs={'user_id': applicant.id,'club_id':self.club.id})
        response = self.client.get(url, follow=True)
        self.club.refresh_from_db()
        applicant_membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id':self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(len(Membership.objects.all().filter(user=self.user.id, club=self.club)), 0)
        self.assertTrue(self.club.is_owner(self.user))
        self.assertFalse(self.club.is_owner(applicant))
        self.assertTrue(applicant_membership.is_applicant())

    def test_owner_cannot_transfer_ownership_to_member(self):
        self.assertTrue(self.club.is_owner(self.user))
        member = User.objects.get(username = "hillaryunderside@example.org")
        member_membership = Membership.objects.all().filter(user=member.id, club=self.club)[0]
        self.assertTrue(member_membership.is_member())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('owner_transfer', kwargs={'user_id': member.id,'club_id':self.club.id})
        response = self.client.get(url, follow=True)
        self.club.refresh_from_db()
        member_membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id':self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(len(Membership.objects.all().filter(user=self.user.id, club=self.club)), 0)
        self.assertTrue(self.club.is_owner(self.user))
        self.assertFalse(self.club.is_owner(member))
        self.assertTrue(member_membership.is_member())

    def test_owner_cannot_transfer_ownership_to_an_inactive_officer(self):
        self.assertTrue(self.club.is_owner(self.user))
        self.assertTrue(self.membership.is_officer())
        self.target_user.is_active = False
        self.target_user.save()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.club.refresh_from_db()
        self.membership.refresh_from_db()
        response_url = reverse('user_list', kwargs={'club_id':self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(len(Membership.objects.all().filter(user=self.user.id, club=self.club)), 0)
        self.assertTrue(self.club.is_owner(self.user))
        self.assertFalse(self.club.is_owner(self.target_user))
        self.assertTrue(self.membership.is_officer())
