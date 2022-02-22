"""Tests of the reinstate deleted user view"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import Membership, User
from clubs.tests.helpers import CreateClubs, reverse_with_next

class ReinstateDeletedUserViewTestCase(TestCase, CreateClubs):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = self.create_one_extended_club("club1", "London", "A chess club")
        self.user = User.objects.get(username='jamesmoth@example.org')
        self.membership = Membership.objects.all().filter(user=self.user, club=self.club)[0]
        self.target_user = User.objects.get(username='removed@example.org')
        self.target_membership = Membership.objects.all().filter(user=self.target_user, club=self.club)[0]
        self.owner = self.club.owner
        self.url = reverse('reinstate_deleted_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})

    def test_reinstate_deleted_user_url(self):
        self.assertEqual(self.url,f'/reinstate_deleted_user/club_id_{self.club.id}/user_id_{self.target_user.id}')

    def test_reinstate_deleted_user_redirects_when_not_logged_in(self):
        url = reverse('reinstate_deleted_user', kwargs={'user_id': self.target_user.id,'club_id':self.club.id})
        redirect_url = reverse_with_next('log_in', url)
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self.membership.is_removed_user())

    def test_officer_cannot_reinstate_an_applicant(self):
        applicant = User.objects.get(username='pollyanatomato@example.org')
        applicant_membership = Membership.objects.all().filter(user=applicant, club=self.club)[0]
        officer = User.objects.get(username='jamesmoth@example.org')
        officer_membership = Membership.objects.all().filter(user=officer, club=self.club)[0]
        self.assertEqual(applicant_membership.club, officer_membership.club)
        self.assertTrue(applicant_membership.is_applicant())
        self.assertTrue(officer_membership.is_officer())
        applicant_membership.level = '0'
        applicant_membership.save()
        applicant.refresh_from_db()
        self.assertTrue(applicant_membership.is_removed_user())
        self.client.login(username=officer.username, password='Password123')
        url = reverse('reinstate_deleted_user', kwargs={'user_id': applicant.id,'club_id':applicant_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':applicant_membership.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        applicant_membership.refresh_from_db()
        self.assertFalse(applicant_membership.is_applicant())

    def test_officer_cannot_reinstate_a_member(self):
        member = User.objects.get(username='hillaryunderside@example.org')
        member_membership = Membership.objects.all().filter(user=member, club=self.club)[0]
        officer = User.objects.get(username='jamesmoth@example.org')
        officer_membership = Membership.objects.all().filter(user=officer, club=self.club)[0]
        self.assertEqual(member_membership.club, officer_membership.club)
        self.assertTrue(member_membership.is_member())
        self.assertTrue(officer_membership.is_officer())
        member_membership.level = '0'
        member_membership.save()
        member_membership.refresh_from_db()
        self.assertTrue(member_membership.is_removed_user())
        self.client.login(username=officer.username, password='Password123')
        url = reverse('reinstate_deleted_user', kwargs={'user_id': member.id,'club_id':member_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':member_membership.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        member_membership.refresh_from_db()
        self.assertFalse(member_membership.is_applicant())

    def test_owner_can_reinstate_an_applicant(self):
        applicant = User.objects.get(username='pollyanatomato@example.org')
        applicant_membership = Membership.objects.all().filter(user=applicant, club=self.club)[0]
        self.assertEqual(applicant_membership.club, self.club)
        self.assertTrue(applicant_membership.is_applicant())
        self.assertTrue(self.club.is_owner(self.owner))
        applicant_membership.level = '0'
        applicant_membership.save()
        applicant.refresh_from_db()
        self.assertTrue(applicant_membership.is_removed_user())
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('reinstate_deleted_user', kwargs={'user_id': applicant.id,'club_id':applicant_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':applicant_membership.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        applicant_membership.refresh_from_db()
        self.assertTrue(applicant_membership.is_applicant())

    def test_owner_can_reinstate_a_member(self):
        member = User.objects.get(username='hillaryunderside@example.org')
        member_membership = Membership.objects.all().filter(user=member, club=self.club)[0]
        self.assertEqual(member_membership.club, self.club)
        self.assertTrue(member_membership.is_member())
        self.assertTrue(self.club.is_owner(self.owner))
        member_membership.level = '0'
        member_membership.save()
        member.refresh_from_db()
        self.assertTrue(member_membership.is_removed_user())
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('reinstate_deleted_user', kwargs={'user_id': member.id,'club_id':member_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':member_membership.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        member_membership.refresh_from_db()
        self.assertTrue(member_membership.is_applicant())

    def test_owner_can_reinstate_an_officer(self):
        officer = User.objects.get(username='jamesmoth@example.org')
        officer_membership = Membership.objects.all().filter(user=officer, club=self.club)[0]
        self.assertEqual(officer_membership.club, self.club)
        self.assertTrue(officer_membership.is_officer())
        self.assertTrue(self.club.is_owner(self.owner))
        officer_membership.level = '0'
        officer_membership.save()
        officer.refresh_from_db()
        self.assertTrue(officer_membership.is_removed_user())
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('reinstate_deleted_user', kwargs={'user_id': officer.id,'club_id':officer_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':officer_membership.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        officer_membership.refresh_from_db()
        self.assertTrue(officer_membership.is_applicant())

    def test_officer_reinstate_user_with_invalid_id(self):
        member = User.objects.get(username='hillaryunderside@example.org')
        member_membership = Membership.objects.all().filter(user=member, club=self.club)[0]
        officer = User.objects.get(username='jamesmoth@example.org')
        officer_membership = Membership.objects.all().filter(user=officer, club=self.club)[0]
        self.assertEqual(member_membership.club, officer_membership.club)
        self.assertTrue(member_membership.is_member())
        self.assertTrue(officer_membership.is_officer())
        member_membership.level = '0'
        member_membership.save()
        member_membership.refresh_from_db()
        self.assertTrue(member_membership.is_removed_user())
        self.client.login(username=officer.username, password='Password123')
        url = reverse('reinstate_deleted_user', kwargs={'user_id': member.id+99999,'club_id':member_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':member_membership.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        member_membership.refresh_from_db()
        self.assertTrue(member_membership.is_removed_user())

    def test_member_cannot_reinstate_an_applicant(self):
        member = User.objects.get(username='hillaryunderside@example.org')
        member_membership = Membership.objects.all().filter(user=member, club=self.club)[0]
        applicant = User.objects.get(username='pollyanatomato@example.org')
        applicant_membership = Membership.objects.all().filter(user=applicant, club=self.club)[0]
        self.assertEqual(member_membership.club, applicant_membership.club)
        self.assertTrue(member_membership.is_member())
        self.assertTrue(applicant_membership.is_applicant())
        applicant_membership.level = '0'
        applicant_membership.save()
        applicant_membership.refresh_from_db()
        self.assertTrue(applicant_membership.is_removed_user())
        self.client.login(username=member.username, password='Password123')
        url = reverse('reinstate_deleted_user', kwargs={'user_id': applicant.id,'club_id':applicant_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':applicant_membership.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        applicant_membership.refresh_from_db()
        self.assertTrue(applicant_membership.is_removed_user())

    def test_member_cannot_reinstate_another_member(self):
        member = User.objects.get(username='hillaryunderside@example.org')
        member_membership = Membership.objects.all().filter(user=member, club=self.club)[0]
        member2 = User.objects.get(username='hillaryunders2ide@example.org')
        member2_membership = Membership.objects.all().filter(user=member2, club=self.club)[0]
        self.assertEqual(member_membership.club, member2_membership.club)
        self.assertTrue(member_membership.is_member())
        self.assertTrue(member2_membership.is_member())
        member2_membership.level = '0'
        member2_membership.save()
        member2_membership.refresh_from_db()
        self.assertTrue(member2_membership.is_removed_user())
        self.client.login(username=member.username, password='Password123')
        url = reverse('reinstate_deleted_user', kwargs={'user_id': member2.id,'club_id':member2_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':member2_membership.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        member2_membership.refresh_from_db()
        self.assertTrue(member2_membership.is_removed_user())

    def test_member_cannot_reinstate_themselves(self):
        member = User.objects.get(username='hillaryunderside@example.org')
        member_membership = Membership.objects.all().filter(user=member, club=self.club)[0]
        self.assertTrue(member_membership.is_member())
        member_membership.level = '0'
        member_membership.save()
        member_membership.refresh_from_db()
        self.assertTrue(member_membership.is_removed_user())
        self.client.login(username=member.username, password='Password123')
        url = reverse('reinstate_deleted_user', kwargs={'user_id': member.id,'club_id':member_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')
        member_membership.refresh_from_db()
        self.assertTrue(member_membership.is_removed_user())

    def test_officer_cannot_reinstate_themselves(self):
        officer = User.objects.get(username='jamesmoth@example.org')
        officer_membership = Membership.objects.all().filter(user=officer, club=self.club)[0]
        self.assertTrue(officer_membership.is_officer())
        officer_membership.level = '0'
        officer_membership.save()
        officer_membership.refresh_from_db()
        self.assertTrue(officer_membership.is_removed_user())
        self.client.login(username=officer.username, password='Password123')
        url = reverse('reinstate_deleted_user', kwargs={'user_id': officer.id,'club_id':officer_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')
        officer_membership.refresh_from_db()
        self.assertTrue(officer_membership.is_removed_user())
