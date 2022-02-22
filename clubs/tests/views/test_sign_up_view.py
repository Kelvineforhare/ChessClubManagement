"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from clubs.forms import SignUpForm
from clubs.models import User, Membership
from clubs.tests.helpers import CreateClubs, LogInTester

class SignUpViewTestCase(TestCase, LogInTester, CreateClubs):
    """Tests of the sign up view."""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('sign_up')
        self.club = self.create_one_club("My Chess Club", "London", "A chess club")
        self.user = User.objects.get(username='jamesmoth@example.org')
        self.membership = Membership.objects.all().filter(user=self.user, club=self.club)[0]
        self.owner = self.club.owner
        self.form_input = {
            'first_name': 'Jim',
            'last_name': 'Anderson',
            'username': 'jimanderson@example.org',
            'bio': 'My bio',
            'chess_level':'1',
            'personal_statement':'I am...',
            'club': '1',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }

    def test_sign_up_url(self):
        self.assertEqual(self.url,'/sign_up/')

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_applicant_get_sign_up_redirects_when_logged_in(self):
        self.membership.level = "1"
        self.membership.save()
        self.assertTrue(self.membership.is_applicant())
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        response_url = reverse('show_club', kwargs={'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_member_get_sign_up_redirects_when_logged_in(self):
        self.membership.level = "2"
        self.membership.save()
        self.assertTrue(self.membership.is_member())
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_officer_get_sign_up_redirects_when_logged_in(self):
        self.assertTrue(self.membership.is_officer())
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_owner_get_sign_up_redirects_when_logged_in(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.client.login(username=self.owner.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_unsuccessful_sign_up(self):
        self.form_input['username'] = 'BAD_USERNAME'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_successful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('show_club', kwargs={'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')
        user = User.objects.get(username='jimanderson@example.org')
        self.assertEqual(user.first_name, 'Jim')
        self.assertEqual(user.last_name, 'Anderson')
        self.assertEqual(user.bio, 'My bio')
        self.assertEqual(user.chess_level, "1")
        self.assertEqual(user.personal_statement, 'I am...')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())

    def test_signed_up_user_is_an_applicant(self):
        response = self.client.post(self.url, self.form_input, follow=True)
        user = User.objects.get(username='jimanderson@example.org')
        membership = Membership.objects.all().filter(user=user, club=self.club)[0]
        self.assertTrue(membership.is_applicant())

    def test_applicant_post_sign_up_redirects_when_logged_in(self):
        self.membership.level = "1"
        self.membership.save()
        self.assertTrue(self.membership.is_applicant())
        self.client.login(username=self.user.username, password="Password123")
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('show_club', kwargs={'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_member_post_sign_up_redirects_when_logged_in(self):
        self.membership.level = "2"
        self.membership.save()
        self.assertTrue(self.membership.is_member())
        self.client.login(username=self.user.username, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_officer_post_sign_up_redirects_when_logged_in(self):
        self.assertTrue(self.membership.is_officer())
        self.client.login(username=self.user.username, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_owner_post_sign_up_redirects_when_logged_in(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.client.login(username=self.owner.username, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
