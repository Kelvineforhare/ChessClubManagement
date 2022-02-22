"""Tests of the show user view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User,Membership
from clubs.tests.helpers import CreateClubs, reverse_with_next, CreateUsers
from with_asserts.mixin import AssertHTMLMixin

class ShowUserViewTestCase(TestCase, CreateClubs, AssertHTMLMixin):
    """Tests of the show user view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = self.create_one_club("club1", "London", "A chess club")
        self.user = User.objects.get(username='jamesmoth@example.org')
        self.membership = Membership.objects.all().filter(user=self.user, club=self.club)[0]
        self.target_user = User.objects.get(username='hillaryunderside@example.org')
        self.target_membership = Membership.objects.all().filter(user=self.target_user, club=self.club)[0]
        self.owner = self.club.owner
        self.url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})

    def test_show_user_url(self):
        self.assertEqual(self.url,f'/user/club_id_{self.club.id}/user_id_{self.target_user.id}')

    def test_show_user_redirects_when_not_logged_in(self):
        url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})
        redirect_url = reverse_with_next('log_in', url)
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_applicant_get_show_user_with_valid_id(self):
        self.membership.level = "1"
        self.membership.save()
        self.assertTrue(self.membership.is_applicant())
        url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(url, follow=True)
        response_url = reverse('show_club', kwargs={'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_member_get_show_user_with_valid_id(self):
        self.membership.level = "2"
        self.membership.save()
        self.assertTrue(self.membership.is_member())
        url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "hillaryunderside@example.org")

    def test_officer_get_show_user_with_valid_id(self):
        self.assertTrue(self.membership.is_officer())
        url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "hillaryunderside@example.org")

    def test_owner_get_show_user_with_valid_id(self):
        self.assertTrue(self.club.is_owner(self.owner))
        url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})
        self.client.login(username=self.owner.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "hillaryunderside@example.org")

    def test_applicant_get_show_user_with_own_id(self):
        self.membership.level = "1"
        self.membership.save()
        self.assertTrue(self.membership.is_applicant())
        url = reverse('show_user', kwargs={'user_id': self.user.id, 'club_id' : self.club.id})
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(url, follow=True)
        response_url = reverse('show_club', kwargs={'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_member_get_show_user_with_own_id(self):
        self.membership.level = "2"
        self.membership.save()
        self.assertTrue(self.membership.is_member())
        url = reverse('show_user', kwargs={'user_id': self.user.id, 'club_id' : self.club.id})
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "James Moth")
        self.assertContains(response, "jamesmoth@example.org")

    def test_officer_get_show_user_with_own_id(self):
        self.assertTrue(self.membership.is_officer())
        url = reverse('show_user', kwargs={'user_id': self.user.id, 'club_id' : self.club.id})
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "James Moth")
        self.assertContains(response, "jamesmoth@example.org")

    def test_owner_get_show_user_with_own_id(self):
        self.assertTrue(self.club.is_owner(self.owner))
        url = reverse('show_user', kwargs={'user_id': self.owner.id, 'club_id' : self.club.id})
        self.client.login(username=self.owner.username, password='Password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "John Smith")
        self.assertContains(response, "johnsmith@example.org")

    def test_applicant_get_show_user_with_invalid_id(self):
        self.membership.level = "1"
        self.membership.save()
        self.assertTrue(self.membership.is_applicant())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.user.id+9999, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('show_club', kwargs={'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_member_get_show_user_with_invalid_id(self):
        self.membership.level = "2"
        self.membership.save()
        self.assertTrue(self.membership.is_member())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.user.id+9999, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_member_get_show_user_with_applicant_id(self):
        self.membership.level = "2"
        self.membership.save()
        self.assertTrue(self.membership.is_member())
        self.target_membership.level = "1"
        self.target_membership.save()
        self.assertTrue(self.target_membership.is_applicant())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_officer_get_show_user_with_invalid_id(self):
        self.assertTrue(self.membership.is_officer())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.user.id+9999, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_owner_get_show_user_with_invalid_id(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.owner.id+9999, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_member_can_see_limited_info_about_other_members(self):
        self.membership.level = "2"
        self.membership.save()
        self.assertTrue(self.membership.is_member())
        self.assertTrue(self.target_membership.is_member())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})
        response = self.client.get(url)
        chess_level_query = f'.//form[@action="{url}"]/p[3]'
        personal_statement_query = f'.//form[@action="{url}"]/p[2]'
        with self.assertHTML(response) as html:
            chess_level = html.find(chess_level_query)
            personal_statement = html.find(personal_statement_query)
            self.assertIsNone(chess_level)
            self.assertIsNone(personal_statement)

    def test_member_can_see_limited_info_about_officers(self):
        self.membership.level = "2"
        self.membership.save()
        self.assertTrue(self.membership.is_member())
        self.target_membership.level = "3"
        self.target_membership.save()
        self.assertTrue(self.target_membership.is_officer())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})
        response = self.client.get(url)
        chess_level_query = f'.//form[@action="{url}"]/p[3]'
        personal_statement_query = f'.//form[@action="{url}"]/p[2]'
        with self.assertHTML(response) as html:
            chess_level = html.find(chess_level_query)
            personal_statement = html.find(personal_statement_query)
            self.assertIsNone(chess_level)
            self.assertIsNone(personal_statement)

    def test_member_can_see_limited_info_about_owner(self):
        self.membership.level = "2"
        self.membership.save()
        self.assertTrue(self.membership.is_member())
        self.assertTrue(self.club.is_owner(self.owner))
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.owner.id, 'club_id' : self.club.id})
        response = self.client.get(url)
        chess_level_query = f'.//form[@action="{url}"]/p[3]'
        personal_statement_query = f'.//form[@action="{url}"]/p[2]'
        with self.assertHTML(response) as html:
            chess_level = html.find(chess_level_query)
            personal_statement = html.find(personal_statement_query)
            self.assertIsNone(chess_level)
            self.assertIsNone(personal_statement)

    def test_officer_can_see_all_info_about_applicants(self):
        self.assertTrue(self.membership.is_officer())
        self.target_membership.level = "1"
        self.target_membership.save()
        self.assertTrue(self.target_membership.is_applicant())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})
        response = self.client.get(url)
        chess_level_query = f'.//form[@action="{url}"]/p[3]'
        personal_statement_query = f'.//form[@action="{url}"]/p[2]'
        with self.assertHTML(response) as html:
            chess_level = html.find(chess_level_query)
            personal_statement = html.find(personal_statement_query)
            self.assertEquals(chess_level.text, "Chess level: Grand Master")
            self.assertEquals(personal_statement.text, "Personal Statement: Chess")

    def test_officer_can_see_all_info_about_members(self):
        self.assertTrue(self.membership.is_officer())
        self.assertTrue(self.target_membership.is_member())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})
        response = self.client.get(url)
        chess_level_query = f'.//form[@action="{url}"]/p[3]'
        personal_statement_query = f'.//form[@action="{url}"]/p[2]'
        with self.assertHTML(response) as html:
            chess_level = html.find(chess_level_query)
            personal_statement = html.find(personal_statement_query)
            self.assertEquals(chess_level.text, "Chess level: Grand Master")
            self.assertEquals(personal_statement.text, "Personal Statement: Chess")

    def test_officer_can_see_limited_info_about_other_officers(self):
        self.assertTrue(self.membership.is_officer())
        self.target_membership.level = "3"
        self.target_membership.save()
        self.assertTrue(self.target_membership.is_officer())
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})
        response = self.client.get(url)
        chess_level_query = f'.//form[@action="{url}"]/p[3]'
        personal_statement_query = f'.//form[@action="{url}"]/p[2]'
        with self.assertHTML(response) as html:
            chess_level = html.find(chess_level_query)
            personal_statement = html.find(personal_statement_query)
            self.assertIsNone(chess_level)
            self.assertIsNone(personal_statement)

    def test_officer_can_see_limited_info_about_owner(self):
        self.assertTrue(self.membership.is_officer())
        self.assertTrue(self.club.is_owner(self.owner))
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.owner.id, 'club_id' : self.club.id})
        response = self.client.get(url)
        chess_level_query = f'.//form[@action="{url}"]/p[3]'
        personal_statement_query = f'.//form[@action="{url}"]/p[2]'
        with self.assertHTML(response) as html:
            chess_level = html.find(chess_level_query)
            personal_statement = html.find(personal_statement_query)
            self.assertIsNone(chess_level)
            self.assertIsNone(personal_statement)

    def test_owner_can_see_all_info_about_applicants(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.target_membership.level = "1"
        self.target_membership.save()
        self.assertTrue(self.target_membership.is_applicant())
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})
        response = self.client.get(url)
        chess_level_query = f'.//form[@action="{url}"]/p[3]'
        personal_statement_query = f'.//form[@action="{url}"]/p[2]'
        with self.assertHTML(response) as html:
            chess_level = html.find(chess_level_query)
            personal_statement = html.find(personal_statement_query)
            self.assertEquals(chess_level.text, "Chess level: Grand Master")
            self.assertEquals(personal_statement.text, "Personal Statement: Chess")

    def test_owner_can_see_all_info_about_members(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.assertTrue(self.target_membership.is_member())
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})
        response = self.client.get(url)
        chess_level_query = f'.//form[@action="{url}"]/p[3]'
        personal_statement_query = f'.//form[@action="{url}"]/p[2]'
        with self.assertHTML(response) as html:
            chess_level = html.find(chess_level_query)
            personal_statement = html.find(personal_statement_query)
            self.assertEquals(chess_level.text, "Chess level: Grand Master")
            self.assertEquals(personal_statement.text, "Personal Statement: Chess")

    def test_owner_can_see_all_info_about_officers(self):
        self.assertTrue(self.club.is_owner(self.owner))
        self.target_membership.level = "3"
        self.target_membership.save()
        self.assertTrue(self.target_membership.is_officer())
        self.client.login(username=self.owner.username, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id' : self.club.id})
        response = self.client.get(url)
        chess_level_query = f'.//form[@action="{url}"]/p[3]'
        personal_statement_query = f'.//form[@action="{url}"]/p[2]'
        with self.assertHTML(response) as html:
            chess_level = html.find(chess_level_query)
            personal_statement = html.find(personal_statement_query)
            self.assertEquals(chess_level.text, "Chess level: Grand Master")
            self.assertEquals(personal_statement.text, "Personal Statement: Chess")
