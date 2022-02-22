"""Tests for the profile view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.forms import UserForm
from clubs.models import User, Membership
from clubs.tests.helpers import reverse_with_next, CreateClubs

class ProfileViewTestCase(TestCase, CreateClubs):
    """Test suite for the profile view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = self.create_one_club("club1", "London", "A chess club")
        self.user = User.objects.get(username='jamesmoth@example.org')
        self.membership = Membership.objects.all().filter(user=self.user, club=self.club)[0]
        self.owner = self.club.owner
        self.url = reverse('profile')
        self.form_input = {
            'first_name': 'James2',
            'last_name': 'Moth2',
            'username': 'new_username@example.org',
            'bio': 'Hi, im James2.',
            'chess_level': "3",
            'personal_statement':'I love chess2!',
        }

    def test_profile_url(self):
        self.assertEqual(self.url, '/profile/')
    
    def test_get_profile(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertEqual(form.instance, self.user)
    
    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_applicant_successful_profile_update(self):
        self.membership.level = "1"
        self.membership.save()
        self.assertTrue(self.membership.is_applicant())
        self.client.login(username=self.user.username, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'new_username@example.org')
        self.assertEqual(self.user.first_name, 'James2')
        self.assertEqual(self.user.last_name, 'Moth2')
        self.assertEqual(self.user.bio, 'Hi, im James2.')


    def test_member_successful_profile_update(self):
        self.membership.level = "2"
        self.membership.save()
        self.assertTrue(self.membership.is_member())
        self.client.login(username=self.user.username, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'new_username@example.org')
        self.assertEqual(self.user.first_name, 'James2')
        self.assertEqual(self.user.last_name, 'Moth2')
        self.assertEqual(self.user.bio, 'Hi, im James2.')

    def test_officer_successful_profile_update(self):
        self.membership.level = "3"
        self.membership.save()
        self.assertTrue(self.membership.is_officer())
        self.client.login(username=self.user.username, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'new_username@example.org')
        self.assertEqual(self.user.first_name, 'James2')
        self.assertEqual(self.user.last_name, 'Moth2')
        self.assertEqual(self.user.bio, 'Hi, im James2.')

    
    def test_owner_successful_profile_update(self):
        self.membership.level = "4"
        self.membership.save()
        self.assertTrue(self.membership.level == "4")
        self.client.login(username=self.user.username, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'new_username@example.org')
        self.assertEqual(self.user.first_name, 'James2')
        self.assertEqual(self.user.last_name, 'Moth2')
        self.assertEqual(self.user.bio, 'Hi, im James2.')
    
    def test_unsuccessful_profile_update_due_to_bad_username(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['username'] = 'BAD_USERNAME'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'jamesmoth@example.org')
    
    def test_unsuccessful_profile_update_due_to_duplicate_username(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['username'] = 'hillaryunderside@example.org'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'jamesmoth@example.org')
    
    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
