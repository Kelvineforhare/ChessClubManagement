"""Tests of the user list view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User,Membership
from clubs.tests.helpers import reverse_with_next, CreateClubs

class UserListViewTestCase(TestCase, CreateClubs):

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):

        self.club = self.create_one_club("club1", "London", "A chess club")
        self.user = User.objects.get(username='jamesmoth@example.org')
        self.membership = Membership.objects.all().filter(user=self.user, club=self.club)[0]
        self.owner = self.club.owner
        self.url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.test_user_num = 5

    def test_user_list_url(self):
        self.assertEqual(self.url,f'/users/club_id_{self.club.id}')

    def test_user_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_applicant_get_user_list(self):
        self.membership.level = "1"
        self.membership.save()
        self.assertTrue(self.membership.is_applicant())
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_member_get_user_list(self):
        self.membership.level = "2"
        self.membership.save()
        self.assertTrue(self.membership.is_member())
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_users(self.test_user_num)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self._no_applicants_shown(response, self.test_user_num)
        self._all_members_shown(response, self.test_user_num)
        self._all_officers_shown(response, self.test_user_num)
        self._owner_shown(response)

    def test_officer_get_user_list(self):
        self.assertTrue(self.membership.is_officer())
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_users(self.test_user_num)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self._all_applicants_shown(response, self.test_user_num)
        self._all_members_shown(response, self.test_user_num)
        self._all_officers_shown(response, self.test_user_num)
        self._owner_shown(response)

    def test_owner_get_user_list(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.client.login(username=self.owner.username, password='Password123')
        self._create_test_users(self.test_user_num)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self._all_applicants_shown(response, self.test_user_num)
        self._all_members_shown(response, self.test_user_num)
        self._all_officers_shown(response, self.test_user_num)

    def test_user_list_only_shows_active_users(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.client.login(username=self.owner.username, password='Password123')
        self._create_test_users(self.test_user_num)
        self._create_inactive_user()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertNotContains(response, 'inactive@example.org')
        self.assertNotContains(response, 'Inac')
        self.assertNotContains(response, 'Tive')
        user = User.objects.get(username='inactive@example.org')
        user_url = reverse('show_user', kwargs={'club_id': self.club.id, 'user_id': user.id})
        self.assertNotContains(response, user_url)

    def _create_test_users(self, user_count=10):
        self._create_test_applicants(user_count)
        self._create_test_members(user_count)
        self._create_test_officers(user_count)

    def _create_test_applicants(self, user_count=10):
        for user_id in range(user_count):
            username = f'user{user_id}@applicants.org'
            first_name = f'First{user_id}app'
            last_name=f'Last{user_id}app'
            user = self.create_user(username, first_name, last_name)
            membership = Membership(
                   user = user,
                   club = self.club,
                   level = "1"
            )
            membership.save()
            self.club.members.add(user)

    def _create_test_members(self, user_count=10):
        for user_id in range(user_count):
            username = f'user{user_id}@members.org'
            first_name = f'First{user_id}mem'
            last_name=f'Last{user_id}mem'
            user = self.create_user(username, first_name, last_name)
            membership = Membership(
                   user = user,
                   club = self.club,
                   level = "2"
            )
            membership.save()
            self.club.members.add(user)

    def _create_test_officers(self, user_count=10):
        for user_id in range(user_count):
            username = f'user{user_id}@officers.org'
            first_name = f'First{user_id}off'
            last_name=f'Last{user_id}off'
            user = self.create_user(username, first_name, last_name)
            membership = Membership(
                   user = user,
                   club = self.club,
                   level = "3"
            )
            membership.save()
            self.club.members.add(user)

    def _all_applicants_shown(self, response, user_num):
        for user_id in range(user_num):
            self.assertContains(response, f'First{user_id}app')
            self.assertContains(response, f'Last{user_id}app')
            user = User.objects.get(username=f'user{user_id}@applicants.org')
            user_url = reverse('show_user', kwargs={'club_id': self.club.id, 'user_id': user.id})
            self.assertContains(response, user_url)

    def _no_applicants_shown(self, response, user_num):
        for user_id in range(user_num):
            self.assertNotContains(response, f'First{user_id}app')
            self.assertNotContains(response, f'Last{user_id}app')
            user = User.objects.get(username=f'user{user_id}@applicants.org')
            user_url = reverse('show_user', kwargs={'club_id': self.club.id, 'user_id': user.id})
            self.assertNotContains(response, user_url)

    def _all_members_shown(self, response, user_num):
        for user_id in range(user_num):
            self.assertContains(response, f'First{user_id}mem')
            self.assertContains(response, f'Last{user_id}mem')
            user = User.objects.get(username=f'user{user_id}@members.org')
            user_url = reverse('show_user', kwargs={'club_id': self.club.id, 'user_id': user.id})
            self.assertContains(response, user_url)

    def _all_officers_shown(self, response, user_num):
        for user_id in range(user_num):
            self.assertContains(response, f'First{user_id}off')
            self.assertContains(response, f'Last{user_id}off')
            user = User.objects.get(username=f'user{user_id}@officers.org')
            user_url = reverse('show_user', kwargs={'club_id': self.club.id, 'user_id': user.id})
            self.assertContains(response, user_url)

    def _owner_shown(self, response):
        self.assertContains(response, self.owner.username)
        self.assertContains(response, self.owner.first_name)
        self.assertContains(response, self.owner.last_name)
        user = User.objects.get(username=self.owner.username)
        user_url = reverse('show_user', kwargs={'club_id': self.club.id, 'user_id': user.id})
        self.assertContains(response, user_url)

    def _create_inactive_user(self):
        username = 'inactive@example.org'
        first_name = 'Inac'
        last_name ='Tive'
        user = self.create_user(username, first_name, last_name)
        membership = Membership(
               user = user,
               club = self.club,
               level = "2"
        )
        membership.save()
        self.club.members.add(user)
        user.is_active = False
        user.save()
