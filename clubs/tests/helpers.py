from django.urls import reverse
from clubs.models import User, Club, Membership
from django.contrib.auth.models import Group
from with_asserts.mixin import AssertHTMLMixin

def reverse_with_next(url_name, next_url):
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url

class CreateUsers:

    def create_user(self, username_in, first_name_in, last_name_in):
        user = User.objects.create_user(
                    first_name = first_name_in,
                    last_name = last_name_in,
                    username = username_in,
                    bio = "My name is..." ,
                    personal_statement = "Chess",
                    chess_level = "4",
                    password = "Password123"
                )

        user.save()
        return user

class CreateClubs(CreateUsers):

    def create_one_club(self, name_in, location_in, description_in):
        owner = self.create_user("johnsmith@example.org", "John", "Smith")
        officer = self.create_user("jamesmoth@example.org", "James", "Moth")
        member = self.create_user("hillaryunderside@example.org", "Hillary", "Underside")
        applicant = self.create_user("pollyanatomato@example.org", "Pollyana", "Tomato")
        return self.create_club(name_in, location_in, description_in, owner, officer, member, applicant)

    def create_club(self, name_in, location_in, description_in, owner, officer, member, applicant):

        club_object = Club(
            owner=owner,
            name = name_in,
            location = location_in,
            description = description_in
        )
        club = Group.objects.get_or_create(name=club_object.name)

        club_object.save()

        membership = Membership(
               user = officer,
               club = club_object,
                level = "3"
            )
        membership.save()
        club_object.members.add(officer)

        membership = Membership(
               user = member,
               club = club_object,
                level = "2"
            )
        membership.save()
        club_object.members.add(member)

        membership = Membership(
               user = applicant,
               club = club_object,
                level = "1"
            )
        membership.save()
        club_object.members.add(applicant)

        return club_object


    def create_one_extended_club(self, name_in, location_in, description_in):
        owner = self.create_user("johnsmith@example.org", "John", "Smith")
        officer = self.create_user("jamesmoth@example.org", "James", "Moth")
        officer2 = self.create_user("jamesmoth2@example.org", "James", "Moth")
        member = self.create_user("hillaryunderside@example.org", "Hillary", "Underside")
        member2 = self.create_user("hillaryunders2ide@example.org", "Hillary", "Underside")
        applicant = self.create_user("pollyanatomato@example.org", "Pollyana", "Tomato")
        removed = self.create_user("removed@example.org", "Bob", "Dylan")
        return self.create_extended_club(name_in, location_in, description_in, owner, officer,officer2 , member,member2, applicant,removed)

    def create_extended_club(self, name_in, location_in, description_in, owner, officer,officer2 , member,member2, applicant,removed):

        club_object = Club(
            owner=owner,
            name = name_in,
            location = location_in,
            description = description_in
        )
        club = Group.objects.get_or_create(name=club_object.name)

        club_object.save()

        membership = Membership(
               user = officer,
               club = club_object,
                level = "3"
            )
        membership.save()
        club_object.members.add(officer)

        membership = Membership(
               user = officer2,
               club = club_object,
                level = "3"
            )
        membership.save()
        club_object.members.add(officer2)

        membership = Membership(
               user = member,
               club = club_object,
                level = "2"
            )
        membership.save()
        club_object.members.add(member)

        membership = Membership(
               user = member2,
               club = club_object,
                level = "2"
            )
        membership.save()
        club_object.members.add(member2)

        membership = Membership(
               user = applicant,
               club = club_object,
                level = "1"
            )
        membership.save()
        club_object.members.add(applicant)

        membership = Membership(
               user = removed,
               club = club_object,
                level = "0"
            )
        membership.save()
        club_object.members.add(removed)

        return club_object

# class CreateMemberships(CreateClubs,CreateUsers):
#     global club


#     def create_owner_membership(self):
#         owner = self.create_user("johnsmith@owner.org", "John", "Smith")
#         club = self.create_one_club("Happy Chess Club", "Strand","WE are good at Chess")
#         membership = Membership(
#                user = owner,
#                club = club,
#                 level = "4"
#             )
#         membership.save()
#         club.members.add(owner)
#         return membership

#     def create_officer_membership(self):
#         officer = self.create_user("jamesmoth@officer.org", "James", "Moth")
#         club = self.create_one_club("Happy Chess Club", "Strand","WE are good at Chess")
#         membership = Membership(
#                user = officer,
#                club = club,
#                 level = "3"
#             )
#         membership.save()
#         club.members.add(officer)
#         return membership

#     def create_member_membership(self):
#         member = self.create_user("hillaryunderside@member.org", "Hillary", "Underside")
#         club = self.create_one_club("Happy Chess Club", "Strand","WE are good at Chess")
#         membership = Membership(
#                user = member,
#                club = club,
#                 level = "2"
#             )
#         membership.save()
#         club.members.add(member)
#         return membership

#     def create_applicant_membership(self):
#         applicant = self.create_user("pollyanatomato@applicant.org", "Pollyana", "Tomato")
#         club = self.create_one_club("Happy Chess Club", "Strand","WE are good at Chess")
#         membership = Membership(
#                user = applicant,
#                club = club,
#                 level = "1"
#             )
#         membership.save()
#         club.members.add(applicant)
#         return membership

#     def create_removed_membership(self):
#         left = self.create_user("removed@left.org", "Polly", "Annie")
#         club = self.create_one_club("Happy Chess Club", "Strand","WE are good at Chess")
#         membership = Membership(
#                user = left,
#                club = club,
#                 level = "0"
#             )
#         membership.save()
#         club.members.add(left)
#         return membership

class LogInTester:
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()

class MenuTesterMixin(AssertHTMLMixin):
    menu_urls = [reverse('home'), reverse('profile'),reverse('log_out'),reverse('password')]

    def assert_menu(self, response):
        for url in self.menu_urls:
            with self.assertHTML(response, f'a[href="{url}"]'):
                pass
            
    def assert_restricted_menu(self, response):
        for url in self.menu_urls:
            if url != reverse('user_list', kwargs={'club_id': self.club.id}):
                with self.assertHTML(response, f'a[href="{url}"]'):
                    pass

    def assert_no_menu(self, response):
        for url in self.menu_urls:
            self.assertNotHTML(response, f'a[href="{url}"]')
