"""Tests of the create club view"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club
from clubs.forms import CreateClubForm
from clubs.tests.helpers import CreateClubs, reverse_with_next
from django.contrib import messages

class CreateClubViewTestCase(TestCase, CreateClubs):
    """Tests of the create club view"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = self.create_one_club("John's Club", "Strand", "This is a club")
        self.user = User.objects.get(username='hillaryunderside@example.org')
        self.url = reverse('create_club')
        self.form_input = {
            'name': 'New Club',
            'location': 'Kensington',
            'description': 'A new chess club.'
        }

    def test_create_club_url(self):
        self.assertEqual(self.url,'/create_club/')

    def test_create_club_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_create_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateClubForm))
        self.assertFalse(form.is_bound)

    def test_successful_create_club(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count+1)
        new_club = Club.objects.get(name='New Club')
        response_url = reverse('user_list', kwargs={'club_id': new_club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(new_club.name, 'New Club')
        self.assertEqual(new_club.location, 'Kensington')
        self.assertEqual(new_club.description, 'A new chess club.')

    def test_unsuccessful_create_club(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['name'] = 'x' * 51
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateClubForm))
        self.assertTrue(form.is_bound)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_unsuccessful_create_club_due_to_duplicate_club_name(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['name'] = self.club.name
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateClubForm))
        self.assertTrue(form.is_bound)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_create_club_with_blank_club_name(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['name'] = ''
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateClubForm))
        self.assertTrue(form.is_bound)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_create_club_with_blank_club_location(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['location'] = ''
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateClubForm))
        self.assertTrue(form.is_bound)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_create_club_with_blank_club_description(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['description'] = ''
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateClubForm))
        self.assertTrue(form.is_bound)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
