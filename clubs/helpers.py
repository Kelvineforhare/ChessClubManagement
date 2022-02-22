"""Decorators used on the view functions"""
from django.shortcuts import redirect
from django.conf import settings
from .models import Club, Membership
from django.contrib import messages

def login_prohibited(view_function):
    def wrapper_func(request, *args, **kwargs):
        current_user = request.user
        if current_user.is_authenticated and not current_user.is_superuser:
            clubs=Club.objects.all()
            club=[club for club in clubs if club.is_part_of(current_user)]
            if(len(club) >= 1):
                club = club[0]
            else:
                club = clubs[0]
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN, club_id=club.id)
        else:
            return view_function(request)
    return wrapper_func

def member_or_above_required(view_function, *args, **kwargs):
    def wrapper_func(request, *args, **kwargs):
        club_id = kwargs['club_id']
        current_user = request.user
        clubs=Club.objects.all()
        club=clubs.get(pk=club_id)
        if(club.is_owner(current_user)):
            return view_function(request, *args, **kwargs)
        membership = Membership.objects.all().filter(user=current_user, club=club)
        if membership and not membership[0].is_applicant() and not membership[0].is_removed_user():
            return view_function(request, *args, **kwargs)
        else:
            return redirect('show_club',club_id)
    return wrapper_func

def officer_or_above_required(view_function, *args, **kwargs):
    def wrapper_func(request, *args, **kwargs):
        club_id = kwargs['club_id']
        current_user = request.user
        clubs=Club.objects.all()
        club=clubs.filter(pk=club_id)[0]
        if club.is_owner(current_user):
            return view_function(request, *args, **kwargs)
        membership = Membership.objects.all().filter(user=current_user, club=club)[0]

        if (membership.is_officer()):
            return view_function(request, *args, **kwargs)
        else:
            return redirect('profile')
    return wrapper_func

def owner_required(view_function):
    def wrapper_func(request, *args, **kwargs):
        club_id = kwargs['club_id']
        current_user = request.user
        club=Club.objects.get(pk=club_id)

        if (club.is_owner(current_user)):
            return view_function(request, *args, **kwargs)
        else:
            return redirect('user_list', club_id)
    return wrapper_func

def owner_prohibited(view_function):
    def wrapper_func(request, *args, **kwargs):
        club_id = kwargs['club_id']
        clubs=Club.objects.all()
        club=clubs.filter(pk=club_id)[0]
        current_user = request.user
        if (not club.is_owner(current_user)):
            return view_function(request, *args, **kwargs)
        else:
            messages.error(request,"Owner cannot do this")
            return redirect('user_list',club.id)
    return wrapper_func
