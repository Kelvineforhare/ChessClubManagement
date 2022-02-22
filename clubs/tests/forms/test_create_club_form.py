"""Unit tests of the create club in form."""
from django.test import TestCase
from clubs.forms import CreateClubForm
from clubs.models import User, Club
from clubs.tests.helpers import CreateClubs

class CreateClubFormTestCase(TestCase, CreateClubs):
    """Unit tests of the create club form."""

    fixtures = ['clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.club = self.create_one_club("club1", "London", "A chess club")
        self.user = User.objects.get(username='jamesmoth@example.org')
        self.form_input = {
            'name': 'Test Club',
            'location': 'Kensington',
            'description': 'A test chess club.'
        }

    def test_form_contains_required_fields(self):
        form = CreateClubForm()
        self.assertIn('name', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('description', form.fields)

    def test_form_uses_model_validation(self):
        self.form_input['name'] = ''
        form = CreateClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_valid_create_club_form(self):
        form = CreateClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_name(self):
        self.form_input['name'] = ''
        form = CreateClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_location(self):
        self.form_input['location'] = ''
        form = CreateClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_description(self):
        self.form_input['description'] = ''
        form = CreateClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = CreateClubForm(instance=self.user, data=self.form_input)
        before_count = Club.objects.count()
        form.save()
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count+1)
        club = Club.objects.get(name=self.form_input['name'])
        self.assertEqual(club.name, 'Test Club')
        self.assertEqual(club.location, 'Kensington')
        self.assertEqual(club.description, 'A test chess club.')
