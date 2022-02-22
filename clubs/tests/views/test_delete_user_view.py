"""Tests of the delete user view"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import Membership, User
from clubs.tests.helpers import reverse_with_next, CreateClubs


class DeleteUserViewTestCase(TestCase, CreateClubs):
    """Tests of the delete user view"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = self.create_one_extended_club("club1", "London", "A chess club")
        self.user = User.objects.get(username='jamesmoth@example.org')
        self.membership = Membership.objects.all().filter(user=self.user, club=self.club)[0]
        self.target_user = User.objects.get(username='hillaryunderside@example.org')
        self.target_membership = Membership.objects.all().filter(user=self.target_user, club=self.club)[0]
        self.owner = self.club.owner
        self.url = reverse('delete_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})

    def test_delete_user_url(self):
        self.assertEqual(self.url,f'/delete_user/club_id_{self.club.id}/user_id_{self.target_user.id}')

    def test_delete_user_redirects_when_not_logged_in(self):
        url = reverse('delete_user', kwargs={'user_id': self.target_user.id,'club_id':self.club.id})
        redirect_url = reverse_with_next('log_in', url)
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self.membership.is_removed_user())

    def test_officer_cannot_delete_an_applicant(self):
        applicant = User.objects.get(username='pollyanatomato@example.org')
        applicant_membership = Membership.objects.all().filter(user=applicant, club=self.club)[0]
        officer = User.objects.get(username='jamesmoth@example.org')
        officer_membership = Membership.objects.all().filter(user=officer, club=self.club)[0]
        self.assertEqual(applicant_membership.club, officer_membership.club)
        self.assertTrue(applicant_membership.is_applicant())
        self.assertTrue(officer_membership.is_officer())
        self.client.login(username=officer.username, password='Password123')
        url = reverse('delete_user', kwargs={'user_id': applicant.id,'club_id':self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':self.club.id})
        self.assertTrue(applicant_membership.is_applicant())
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        applicant_membership.refresh_from_db()
        self.assertFalse(applicant_membership.is_removed_user())

    def test_officer_cannot_delete_a_member(self):
        member = User.objects.get(username='hillaryunderside@example.org')
        member_membership = Membership.objects.all().filter(user=member, club=self.club)[0]
        officer = User.objects.get(username='jamesmoth@example.org')
        officer_membership = Membership.objects.all().filter(user=officer, club=self.club)[0]
        self.assertEqual(member_membership.club, officer_membership.club)
        self.assertTrue(member_membership.is_member())
        self.assertTrue(officer_membership.is_officer())
        self.client.login(username=officer.username, password='Password123')
        url = reverse('delete_user', kwargs={'user_id': member.id,'club_id':self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        member_membership.refresh_from_db()
        self.assertFalse(member_membership.is_removed_user())

    def test_owner_can_delete_an_applicant(self):
        applicant = User.objects.get(username='pollyanatomato@example.org')
        applicant_membership = Membership.objects.all().filter(user=applicant, club=self.club)[0]
        self.assertTrue(applicant_membership.club.is_owner(self.owner))
        self.assertTrue(applicant_membership.is_applicant())
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('delete_user', kwargs={'user_id': applicant.id,'club_id':self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        applicant_membership.refresh_from_db()
        self.assertTrue(applicant_membership.is_removed_user())

    def test_owner_can_delete_a_member(self):
        member = User.objects.get(username='hillaryunderside@example.org')
        member_membership = Membership.objects.all().filter(user=member, club=self.club)[0]
        self.assertTrue(member_membership.club.is_owner(self.owner))
        self.assertTrue(member_membership.is_member())
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('delete_user', kwargs={'user_id': member.id,'club_id':self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        member_membership.refresh_from_db()
        self.assertTrue(member_membership.is_removed_user())

    def test_owner_can_delete_an_officer(self):
        officer = User.objects.get(username='jamesmoth@example.org')
        officer_membership = Membership.objects.all().filter(user=officer, club=self.club)[0]

        self.assertTrue(officer_membership.club.is_owner(self.owner))
        self.assertTrue(officer_membership.is_officer())
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('delete_user', kwargs={'user_id': officer.id,'club_id':officer_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':officer_membership.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        officer_membership.refresh_from_db()
        self.assertTrue(officer_membership.is_removed_user())

    def test_officer_delete_user_with_invalid_id(self):
        applicant = User.objects.get(username='pollyanatomato@example.org')
        applicant_membership = Membership.objects.all().filter(user=applicant, club=self.club)[0]
        officer = User.objects.get(username='jamesmoth@example.org')
        officer_membership = Membership.objects.all().filter(user=officer, club=self.club)[0]
        self.assertTrue(applicant_membership.is_applicant())
        self.assertTrue(officer_membership.is_officer())
        self.client.login(username=officer.username, password='Password123')
        url = reverse('delete_user', kwargs={'user_id': applicant.id+9999,'club_id':officer_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':officer_membership.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_member_cannot_delete_an_applicant(self):
        applicant = User.objects.get(username='pollyanatomato@example.org')
        applicant_membership = Membership.objects.all().filter(user=applicant, club=self.club)[0]
        member = User.objects.get(username='hillaryunderside@example.org')
        member_membership = Membership.objects.all().filter(user=member, club=self.club)[0]
        self.assertTrue(applicant_membership.is_applicant())
        self.assertTrue(member_membership.is_member())
        self.assertEqual(applicant_membership.club, member_membership.club)
        self.client.login(username=member.username, password='Password123')
        url = reverse('delete_user', kwargs={'user_id': applicant.id,'club_id':applicant_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':member_membership.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        applicant.refresh_from_db()
        self.assertTrue(applicant_membership.is_applicant())

    def test_member_cannot_delete_another_member(self):
        member = User.objects.get(username='hillaryunderside@example.org')
        member_membership = Membership.objects.all().filter(user=member, club=self.club)[0]

        member2 = User.objects.get(username='hillaryunders2ide@example.org')
        member_membership2 = Membership.objects.all().filter(user=member2, club=self.club)[0]

        self.assertTrue(member_membership.is_member())
        self.assertTrue(member_membership2.is_member())
        self.assertEqual(member_membership.club, member_membership2.club)
        self.client.login(username=member.username, password='Password123')
        url = reverse('delete_user', kwargs={'user_id': member2.id,'club_id':member_membership2.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':member_membership2.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        member.refresh_from_db()
        self.assertTrue(member_membership2.is_member())

    def test_officer_cannot_delete_another_officer(self):
        officer = User.objects.get(username='jamesmoth@example.org')
        officer_membership = Membership.objects.all().filter(user=officer, club=self.club)[0]
        officer2 = User.objects.get(username='jamesmoth2@example.org')
        officer_membership2 = Membership.objects.all().filter(user=officer, club=self.club)[0]
        self.assertTrue(officer_membership.is_officer())
        self.assertTrue(officer_membership2.is_officer())
        self.assertEqual(officer_membership.club, officer_membership2.club)
        self.client.login(username=officer.username, password='Password123')
        url = reverse('delete_user', kwargs={'user_id': officer2.id,'club_id':officer_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':officer_membership.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        officer2.refresh_from_db()
        self.assertFalse(officer_membership2.is_removed_user())

    def test_officer_cannot_delete_the_owner(self):
        officer = User.objects.get(username='jamesmoth@example.org')
        officer_membership = Membership.objects.all().filter(user=officer, club=self.club)[0]
        self.assertTrue(officer_membership.club.is_owner(self.owner))
        self.assertTrue(officer_membership.is_officer())
        self.client.login(username=officer.username, password='Password123')
        url = reverse('delete_user', kwargs={'user_id': self.owner.id,'club_id':officer_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':officer_membership.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        officer.refresh_from_db()
        self.assertFalse(officer_membership.is_removed_user())

    def test_member_cannot_delete_themselves(self):
        member = User.objects.get(username='hillaryunderside@example.org')
        member_membership = Membership.objects.all().filter(user=member, club=self.club)[0]
        self.assertTrue(member_membership.is_member())
        self.client.login(username=member.username, password='Password123')
        url = reverse('delete_user', kwargs={'user_id': member.id,'club_id':member_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':member_membership.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        member.refresh_from_db()
        self.assertFalse(member_membership.is_removed_user())

    def test_officer_cannot_delete_themselves(self):
        officer = User.objects.get(username='jamesmoth@example.org')
        officer_membership = Membership.objects.all().filter(user=officer, club=self.club)[0]

        self.assertTrue(officer_membership.is_officer())
        self.client.login(username=officer.username, password='Password123')
        url = reverse('delete_user', kwargs={'user_id': officer.id,'club_id':officer_membership.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':officer_membership.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        officer.refresh_from_db()
        self.assertFalse(officer_membership.is_removed_user())

    def test_owner_cannot_delete_themselves(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('delete_user', kwargs={'user_id': self.owner.id,'club_id':self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id':self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.owner.refresh_from_db()
        self.assertTrue(self.club.is_owner(self.owner))
