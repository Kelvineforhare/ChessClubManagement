"""Tests of the log in view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.forms import LogInForm
from clubs.models import User, Membership
from clubs.tests.helpers import CreateClubs, LogInTester, MenuTesterMixin, reverse_with_next

class LogInViewTestCase(TestCase, LogInTester, CreateClubs, MenuTesterMixin):
    """Tests of the log in view."""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.club = self.create_one_club("club1", "London", "A chess club")
        self.url = reverse('log_in')
        self.user = User.objects.get(username='jamesmoth@example.org')
        self.membership = Membership.objects.all().filter(user=self.user, club=self.club)[0]

    def test_log_in_url(self):
        self.assertEqual(self.url,'/log_in/')

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(next)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_get_log_in_with_redirect(self):
        # All groups of users can access their change profile page
        destination_url = reverse('profile')
        self.url = reverse_with_next('log_in', destination_url)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertEqual(next, destination_url)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_applicant_get_log_in_redirects_when_logged_in(self):
        self.membership.level = "1"
        self.membership.save()
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        response_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_member_get_log_in_redirects_when_logged_in(self):
        self.membership.level = "2"
        self.membership.save()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_officer_get_log_in_redirects_when_logged_in(self):
        self.membership.level = "3"
        self.membership.save()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_owner_get_log_in_redirects_when_logged_in(self):
        self.client.login(username=self.club.owner.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_unsuccessful_log_in(self):
        form_input = { 'username': 'johndoe@example.org', 'password': 'WrongPassword123' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_username(self):
        form_input = { 'username': '', 'password': 'Password123' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_password(self):
        form_input = { 'username': 'johndoe@example.org', 'password': '' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_applicant_successful_log_in(self):
        self.membership.level = "1"
        self.membership.save()
        form_input = { 'username': self.user.username, 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
        self.assert_restricted_menu(response)

    def test_member_successful_log_in(self):
        self.membership.level = "2"
        self.membership.save()
        form_input = { 'username': self.user.username, 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
        self.assert_menu(response)

    def test_officer_successful_log_in(self):
        self.membership.level = "3"
        self.membership.save()
        form_input = { 'username': self.user.username, 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
        self.assert_menu(response)

    def test_owner_successful_log_in(self):
        form_input = { 'username': self.club.owner.username, 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
        self.assert_menu(response)

    def test_successful_log_in_with_redirect(self):
        # All user groups can access change password view.
        redirect_url = reverse('password')
        form_input = { 'username': self.user.username, 'password': 'Password123', 'next': redirect_url }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'password.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
        self.assert_restricted_menu(response)

    def test_applicant_post_log_in_redirects_when_logged_in(self):
        self.membership.level = "1"
        self.membership.save()
        self.client.login(username=self.user.username, password="Password123")
        form_input = { 'username': 'wronguser@example.org', 'password': 'WrongPassword123' }
        response = self.client.post(self.url, form_input, follow=True)
        response_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')
        self.assert_restricted_menu(response)

    def test_member_post_log_in_redirects_when_logged_in(self):
        self.membership.level = "2"
        self.membership.save()
        self.client.login(username=self.user.username, password='Password123')
        form_input = { 'username': 'wronguser@example.org', 'password': 'WrongPassword123' }
        response = self.client.post(self.url, form_input, follow=True)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assert_menu(response)

    def test_officer_post_log_in_redirects_when_logged_in(self):
        self.membership.level = "3"
        self.membership.save()
        self.client.login(username=self.user.username, password='Password123')
        form_input = { 'username': 'wronguser@example.org', 'password': 'WrongPassword123' }
        response = self.client.post(self.url, form_input, follow=True)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assert_menu(response)

    def test_owner_post_log_in_redirects_when_logged_in(self):
        self.client.login(username=self.club.owner.username, password='Password123')
        form_input = { 'username': 'wronguser@example.org', 'password': 'WrongPassword123' }
        response = self.client.post(self.url, form_input, follow=True)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assert_menu(response)

    def test_post_log_in_with_incorrect_credentials_and_redirect(self):
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        form_input = { 'username': 'johndoe@example.org', 'password': 'WrongPassword123', 'next': redirect_url }
        response = self.client.post(self.url, form_input)
        next = response.context['next']
        self.assertEqual(next, redirect_url)

    def test_valid_log_in_by_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        form_input = { 'username': self.user.username, 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
