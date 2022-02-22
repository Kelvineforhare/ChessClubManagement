from django.core.management.base import BaseCommand
from faker import Faker
from clubs.models import User, Club, Membership

import random

class Command(BaseCommand):
    """The database seeder."""

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def create_user(self, first_name, last_name, username):
        user = User.objects.create_user(
            first_name = first_name,
            last_name = last_name,
            username = username,
            bio = "I live in " + self.faker.address(),
            personal_statement = self.faker.sentence(),
            chess_level = random.randint(1,5),
            password = 'Password123'
        )
        user.save()
        return user

    def create_membership(self, user, club, level):
        membership = Membership(
           user = user,
           club = club,
           level = level
        )
        membership.save()

    def create_club(self, owner):
        club = Club(
            owner=owner,
            name=self.faker.user_name() + " Chess club",
            location=self.faker.address(),
            description=self.faker.sentence()
        )
        club.save()
        return club


    def handle(self, *args, **options):
        #create Jebediah Kerman
        jebediah_user=self.create_user("Jebediah", "Kerman", "jeb@example.org")
        #create Valentina Kerman
        valentina_user=self.create_user("Valentina", "Kerman", "val@example.org")
        #create Billie Kerman
        billie_user=self.create_user("Billie", "Kerman", "billie@example.org")
        #create a owner for Kerbal Chess Club
        kerbal_owner=self.create_user('Gemsbok', 'SEG_Owner', 'gemsbok@owners.org')
        #create Kerbal Chess Club
        kerbal_club=Club(
            owner=kerbal_owner,
            name="Kerbal Chess Club",
            location=self.faker.address(),
            description="This is Kerbal club."
        )
        kerbal_club.save()

        #make Jebediah Kerman a member of kerbal chess club
        self.create_membership(jebediah_user, kerbal_club, '2')
        kerbal_club.members.add(jebediah_user)
        #make Valentina Kerman a member of kerbal chess club
        self.create_membership(valentina_user, kerbal_club, '2')
        kerbal_club.members.add(valentina_user)
        #make Valentina Kerman a member of kerbal chess club
        self.create_membership(billie_user, kerbal_club, '2')
        kerbal_club.members.add(billie_user)

        # Creating 5 additional clubs
        for i in range(3):
            # Each club has one owner
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            username = first_name.lower() + last_name.lower() + "@owners.org"
            owner = None
            if(i != 1):
                owner = self.create_user(first_name, last_name, username)
            else:
                #make Valentina the owner the second additional club
                owner=valentina_user

            club = self.create_club(owner)

            if(i == 0):
                #make Jebediah the officer in the first additional club
                self.create_membership(jebediah_user, club, '3')
                club.members.add(jebediah_user)
            if(i == 2):
                #make Billie the regular member of the third additional club
                self.create_membership(billie_user,club,'2')
                club.members.add(billie_user)

            # Each club has 8 applicants
            for i in range(8):
                first_name = self.faker.first_name()
                last_name = self.faker.last_name()
                username = first_name.lower() + last_name.lower() + "@applicants.org"
                applicant = self.create_user(first_name, last_name, username)
                self.create_membership(applicant, club, "1")
                club.members.add(applicant)

            # Each club has 10 members
            for i in range(10):
                first_name = self.faker.first_name()
                last_name = self.faker.last_name()
                username = first_name.lower() + last_name.lower() + "@members.org"
                member = self.create_user(first_name, last_name, username)
                self.create_membership(member, club, "2")
                club.members.add(member)

            # Each club has 5 officers
            for i in range(5):
                first_name = self.faker.first_name()
                last_name = self.faker.last_name()
                username = first_name.lower() + last_name.lower() + "@officers.org"
                officer = self.create_user(first_name, last_name, username)
                self.create_membership(officer, club, "3")
                club.members.add(officer)

        print("Seeded!")
