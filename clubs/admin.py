from django.contrib import admin
from .models import User, Club, Membership

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'id','username', 'first_name', 'last_name', 'chess_level', 'is_active',
    ]

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for memberships."""

    list_display = [
        'user', 'club', 'level'
    ]

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for clubs."""

    list_display = [
        'name', 'owner', 'location', 'description'
    ]

