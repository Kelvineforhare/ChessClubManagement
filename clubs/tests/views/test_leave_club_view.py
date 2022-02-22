"""Tests of the leave club view"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import Membership, User
from clubs.tests.helpers import reverse_with_next, CreateClubs


class LeaveClubViewTestCase(TestCase, CreateClubs):

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
        self.url = reverse('leave_club', kwargs={'club_id':self.club.id})

    def test_leave_club_url(self):
        self.assertEqual(self.url,f'/leave_club/club_id_{self.club.id}')

    def test_leave_club_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_applicant_leave_club(self):
        applicant = User.objects.get(username='pollyanatomato@example.org')
        applicant_membership = Membership.objects.all().filter(user=applicant, club=self.club)[0]
        self.client.login(username=applicant.username, password='Password123')
        self.assertTrue(applicant_membership.is_applicant())
        url = reverse('leave_club', kwargs={'club_id':self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'profile.html')
        applicant_membership = Membership.objects.all().filter(user=applicant, club=self.club)
        self.assertEqual(len(applicant_membership),0 )
        self.assertFalse(self.club.is_part_of(applicant))


    def test_member_leave_club(self):
        member = User.objects.get(username='hillaryunderside@example.org')
        member_membership = Membership.objects.all().filter(user=member, club=self.club)[0]
        self.client.login(username=member.username, password='Password123')
        self.assertTrue(member_membership.is_member())
        url = reverse('leave_club', kwargs={'club_id':self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'profile.html')
        member_membership = Membership.objects.all().filter(user=member, club=self.club)
        self.assertEqual(len(member_membership),0 )
        self.assertFalse(self.club.is_part_of(member))

    def test_officer_leave_club(self):
        officer = User.objects.get(username='jamesmoth@example.org')
        officer_membership = Membership.objects.all().filter(user=officer, club=self.club)[0]
        self.client.login(username=officer.username, password='Password123')
        self.assertTrue(officer_membership.is_officer())
        url = reverse('leave_club', kwargs={'club_id':self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'profile.html')
        officer_membership = Membership.objects.all().filter(user=officer, club=self.club)
        self.assertEqual(len(officer_membership),0 )
        self.assertFalse(self.club.is_part_of(officer))

    def test_owner_leave_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        self.assertTrue(self.club.is_owner(self.owner))
        url = reverse('leave_club', kwargs={'club_id':self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertTrue(self.club.is_part_of(self.owner))
        self.assertTrue(self.club.is_owner(self.owner))
