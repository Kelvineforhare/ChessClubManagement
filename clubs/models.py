from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar
from system import settings

class User(AbstractUser):

    """The chess level choices"""
    CHESS_CHOICES = (
        ("1", "Beginner"),
        ("2", "Intermediate"),
        ("3", "Master"),
        ("4", "Grand Master"),
        ("5", "Super Grand Master"),
    )

    """User model for all groups which include applicant, member, officer and owner."""
    username = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    bio = models.CharField(max_length=520, blank=True)
    chess_level = models.CharField(
        max_length=12,
        choices=CHESS_CHOICES,
        default="1",
        validators=[
            RegexValidator(regex=r"^[1-5]$", message="Level must be between 1 and 5")
        ],
    )
    personal_statement = models.CharField(max_length=520, blank=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.username)
        gravatar_url = gravatar_object.get_image(size=size, default="identicon")
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

User._meta.get_field("username").verbose_name = "email"


class Club(models.Model):

    name = models.CharField(max_length=50, blank=False, unique = True)
    location = models.CharField(max_length=50, blank=False)
    description = models.CharField(max_length=50, blank=False)

    # The owner is stored in the club and does not have a membership
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        related_name="owner",
    )


    members = models.ManyToManyField(User, through='Membership')

    def is_part_of(self, user):
        return user == self.owner or self.members.filter(pk=user.id)

    def removed_members(self,user):
        self.members.remove(user.id)

    def is_owner(self, user):
        return user == self.owner

    def __str__(self):
        return self.name

class Membership(models.Model):

    MEMBER_CHOICES = (
        ("0","removed_user"),
        ("1","applicant"),
        ("2","member"),
        ("3","officer"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    level = models.CharField(
        max_length=12,
        choices= MEMBER_CHOICES,
        default="1",
    )

    def leave_club(self):
        self.club.removed_members(self.user)
        self.delete()

    def is_removed_user(self):
        return self.level == "0"

    def is_applicant(self):
        return self.level == "1"

    def is_member(self):
        return self.level == "2"

    def is_officer(self):
        return self.level == "3"

    def remove_user(self):
         self.level = '0'
         self.save()

    def reinstate_user(self):
        if self.level == "0":
            self.level = '1'
            self.save()
