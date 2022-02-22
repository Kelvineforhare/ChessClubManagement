from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from .forms import LogInForm, UserForm, SignUpForm, PasswordForm, CreateClubForm
from .models import User, Club, Membership
from .helpers import login_prohibited, member_or_above_required, officer_or_above_required, owner_prohibited, owner_required

current_club = None

@login_prohibited
def home(request):
    clubs = Club.objects.all()
    return render(request, "home.html",{'clubs':clubs})

@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        next = request.POST.get('next') or ''
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                clubs=Club.objects.all()
                login(request, user)
                try:
                    # Gets a club the user is part of
                    club=[club for club in clubs if club.is_part_of(user)][0]
                except:
                    # In case the user is not part of any clubs
                    club=[club for club in clubs][0]
                    return redirect('profile')
                
                membership = Membership.objects.all().filter(user=user,club=club)
                # Check if the current user has no membership
                if (len(membership) == 0):
                    if club.is_owner(user):
                        redirect_url = next or 'user_list'
                        return redirect(redirect_url, club_id=club.id)

                if membership[0].is_removed_user():
                    club=[club for club in clubs][0]
                    return redirect('profile')

                redirect_url = next or 'user_list'
                return redirect(redirect_url, club_id=club.id)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    else:
        next = request.GET.get('next') or ''
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form, 'next': next})

@login_prohibited
def sign_up(request):
    global current_club
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            club = Club.objects.all().filter(pk=user.club)[0]
            login(request, user)
            apply(request,club.id)
            current_club=club
            return redirect('user_list',club.pk)
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html',{'form':form})

@login_required
@member_or_above_required
def user_list(request, club_id):
    global current_club
    clubs = Club.objects.all()
    current_club=clubs.get(pk=club_id)
    current_user = request.user
    is_owner=current_club.is_owner(current_user)
    users=current_club.members.all()
    if(current_club.is_owner(current_user)):
        user_membership=None
    else:
        user_membership = Membership.objects.all().filter(user=current_user, club=current_club)[0]

    # Gets the clubs you're a part of
    your_clubs=[   
        club for club in clubs 
            if club.is_part_of(current_user) or club.is_owner(current_user) 
                and not Membership.objects.all().filter(user=current_user, club=club)[0].is_removed_user()
    ]

    other_clubs=list(set(clubs)-set(your_clubs))
    # Get each role's groups
    active_users=[active_user for active_user in users if active_user.is_active]
    non_applicants=[Membership.objects.all().filter(user=non_applicant, club=current_club)[0] for non_applicant in active_users
    if Membership.objects.all().filter(user=non_applicant, club=current_club)[0].level!='1' and not Membership.objects.all().filter(user=non_applicant, club=current_club)[0].is_removed_user() ]
    officers = [Membership.objects.all().filter(user=officer, club=current_club)[0] for officer in active_users if Membership.objects.all().filter(user=officer, club=current_club)[0].is_officer()]
    members = [Membership.objects.all().filter(user=member, club=current_club)[0] for member in active_users if Membership.objects.all().filter(user=member, club=current_club)[0].is_member()]
    applicants = []
    # Prevent hackers from seeing the information in the website tools
    if not current_club.is_owner(current_user):
        if not user_membership.is_member():
            applicants = [Membership.objects.all().filter(user=applicants, club=current_club)[0] for applicants in active_users if Membership.objects.all().filter(user=applicants, club=current_club)[0].is_applicant()]
    else:
        applicants = [Membership.objects.all().filter(user=applicants, club=current_club)[0] for applicants in active_users if Membership.objects.all().filter(user=applicants, club=current_club)[0].is_applicant()]
    removed_members = [Membership.objects.all().filter(user=applicants, club=current_club)[0] for applicants in active_users if Membership.objects.all().filter(user=applicants, club=current_club)[0].is_removed_user()]
    context = {
        'user_membership':user_membership,
        'users':non_applicants,
        'members':members, 'officers':officers,
        'applicants':applicants,
        'current_user':current_user,
        'your_clubs':your_clubs,
        'other_clubs':other_clubs,
        'current_club':current_club,
        'is_owner':is_owner,
        'removed_members':removed_members
    }
    return render(request, 'user_list.html', context)

def log_out(request):
    logout(request)
    return redirect('home')

@login_required
@owner_prohibited
def leave_club(request,club_id):
    current_club=Club.objects.get(id=club_id)
    current_user = request.user
    user_membership = Membership.objects.all().filter(user=current_user,club=current_club)
    if len(user_membership) >= 1:
        user_membership[0].leave_club()
    else:
        messages.error(request,"Cannot leave a club with no membership")
        return redirect('user_list',current_club.id)
    return redirect('profile')

@login_required
def profile(request):
    global current_club
    if (current_club is None):
      current_club = Club.objects.all()[0]
    current_user = request.user
    user_membership=None
    is_owner=False
    user_membership = Membership.objects.all().filter(user=current_user, club=current_club)

    if request.method == 'POST':
        form = UserForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('user_list', current_club.id)
    else:
        clubs=Club.objects.all()
        your_clubs=[club for club in clubs if club.is_part_of(current_user)]
        other_clubs=[club for club in clubs if not club.is_part_of(current_user)]
        form = UserForm(instance=current_user)
        if current_club:
            is_owner=current_club.is_owner(current_user)
        if user_membership.count() == 0:
            user_membership=None
        else:
            clubs=Club.objects.all()
            your_clubs=[
                club for club in clubs 
                    if club.is_part_of(current_user) or club.is_owner(current_user) 
                        and not Membership.objects.all().filter(user=current_user, club=club)[0].is_removed_user()
            ]
            other_clubs=[club for club in clubs if not club.is_part_of(current_user)]
            form = UserForm(instance=current_user)
            if current_club:
                is_owner=current_club.is_owner(current_user)
            if user_membership.count() == 0:
                user_membership=None
            else:
                user_membership = user_membership[0]
            context = {
                'form': form,
                'user_membership': user_membership,
                'current_user':current_user,
                'your_clubs':your_clubs,
                'other_clubs':other_clubs,
                'current_club':current_club,
                'is_owner':is_owner
            }
            return render(
                request,
                'profile.html',
                context
            )

    clubs=Club.objects.all()
    your_clubs=[club for club in clubs if club.is_part_of(current_user)]
    other_clubs=[club for club in clubs if not club.is_part_of(current_user)]
    context = {
        'form': form,
        'user_membership': user_membership,
        'current_user':current_user,
        'your_clubs':your_clubs,
        'other_clubs':other_clubs,
        'current_club':current_club
    }
    return render(
        request,
        'profile.html',
        context
    )

@login_required
@member_or_above_required
def show_user(request,user_id, club_id):
    global current_club
    try:
        user = User.objects.get(id=user_id)
        clubs = Club.objects.all()
        current_club=Club.objects.get(id=club_id)
        viewee_membership = Membership.objects.all().filter(user=user, club=current_club)
        current_user = request.user
        your_clubs=[club for club in clubs if club.is_part_of(current_user)]
        other_clubs=list(set(clubs)-set(your_clubs))
        is_owner=current_club.is_owner(current_user)
        user_membership =  Membership.objects.all().filter(user=current_user, club=current_club)
    except ObjectDoesNotExist:
        return redirect('user_list',current_club.id)
    else:
        if viewee_membership:
            viewee_membership = viewee_membership[0]
        else:
            viewee_membership=None
        if user_membership:
            user_membership = user_membership[0]
        else:
            user_membership=None
        # Prevent a member from viewing an applicant's profile by entering the url
        if(viewee_membership and user_membership):
            if(viewee_membership.is_applicant()):
                if(user_membership.is_member()):
                    messages.error(request,"You are not allowed to view an applicant!")
                    return redirect('user_list', current_club.pk)

        context = {
            'user_membership':user_membership,
            'is_owner':is_owner,
            'viewee_membership': viewee_membership,
            'your_clubs':your_clubs,
            'other_clubs':other_clubs,
            'current_club':current_club,
            'current_user':current_user,
            'user':user
        }
        return render(request, 'show_user.html', context)

@login_required
@owner_required
def delete_user(request, user_id, club_id):
    current_club=Club.objects.get(id=club_id)
    try:
        user = User.objects.get(id=user_id)
        delete_membership =  Membership.objects.all().filter(user=user, club=current_club)
        if (len(delete_membership) == 0 ):
            messages.error(request, "Cannot delete this user")
            return redirect('user_list', current_club.pk)

        if current_club.is_owner(user) or request.user == user:
            if not (delete_membership[0].is_officer() and not current_club.is_owner(user)):
                messages.error(request, "Cannot delete the owner, yourself, or another officer")
                return redirect('user_list', current_club.pk)
            else:
                delete_membership[0].remove_user()
        elif request.user == user:
            messages.error(request,"Cannot delete yourself")
            return redirect('user_list',current_club.pk)
        else:
            delete_membership[0].remove_user()
    except ObjectDoesNotExist:
        return redirect('user_list', current_club.pk)
    else:
        messages.add_message(request, messages.SUCCESS, "Deletion successful!")
        return redirect('user_list', current_club.pk)

@login_required
@owner_required
def reinstate_deleted_user(request, user_id, club_id):
    current_club=Club.objects.get(id=club_id)
    try:
        user = User.objects.get(id=user_id)
        reinstate_membership =  Membership.objects.all().filter(user=user, club=current_club)
        reinstate_membership[0].reinstate_user()
    except ObjectDoesNotExist:
        return redirect('user_list', current_club.pk)
    else:
        messages.add_message(request, messages.SUCCESS, "Reinstated successfully!")
        return redirect('user_list', current_club.pk)

@login_required
def password(request):
    global current_club
    user_membership=None
    is_owner=False
    current_user = request.user
    clubs = Club.objects.all()
    if(current_club):
        is_owner=current_club.is_owner(current_user)
    if request.method == 'POST':
        form = PasswordForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if check_password(password, current_user.password):
                new_password = form.cleaned_data.get('new_password')
                current_user.set_password(new_password)
                current_user.save()
                login(request, current_user)
                messages.add_message(request, messages.SUCCESS, "Password updated!")
                return redirect('user_list', current_club.pk)
            else:
                messages.add_message(request, messages.ERROR, "Invalid current password!")
        else:
                messages.add_message(request, messages.ERROR, "Invalid new password!")
    else:
        form = PasswordForm()
    your_clubs=[club for club in clubs if club.is_part_of(current_user)]
    for club in your_clubs:
        membership = Membership.objects.all().filter(user=current_user, club=club)
        # Checking if they have a membership
        if len(membership) > 0:
            if membership[0].is_removed_user():
                your_clubs.remove(club)
    other_clubs=list(set(clubs)-set(your_clubs))
    if current_club:
        is_owner=current_club.is_owner(current_user)
        user_membership= Membership.objects.all().filter(user=current_user, club=current_club)
    else:
        user_membership=None
    return render(
        request,
        'password.html',
        {
            'is_owner':is_owner,
            'form': form,
            'your_clubs':your_clubs,
            'other_clubs':other_clubs,
            'user_membership':user_membership,
            'current_user':current_user,
            'current_club':current_club
        }
    )

@login_required
@owner_required
def owner_transfer(request, user_id, club_id):
    try:
        current_user = request.user
        user = User.objects.get(id=user_id)
        current_club=Club.objects.get(id=club_id)
        user_membership=None
    except ObjectDoesNotExist:
        return redirect('log_in')
    else:
        if(current_user != user and user.is_active):
            user_membership = Membership.objects.all().filter(user=user, club=current_club)[0]
            if(not user_membership.is_applicant() and not user_membership.is_member()):
                # Remove former owner from owner group and add chosen officers to owner group
                current_membership = Membership(user=current_user, club=current_club, level='3')
                current_membership.save()
                current_club.members.add(current_user)
                # Remove chosen officer from officer group and add former owner to officer group
                current_club.members.remove(user)
                user_membership.delete()
                current_club.owner=user
                current_club.save()
                messages.add_message(request, messages.SUCCESS, "Owner transfer successful!")
            else:
                messages.add_message(request, messages.ERROR, "You can not transfer ownership to applicants or members!")
        else:
            messages.add_message(request, messages.ERROR, "You can not transfer ownership to yourself or an inactive user!")

        return redirect('user_list', current_club.pk)

@login_required
def promote_club_member(request, user_id, club_id):
    try:
        current_club=Club.objects.get(id=club_id)
        current_user = request.user
        user = User.objects.get(id=user_id)
        is_part_of = current_club.is_part_of(user)
        is_owner = current_club.is_owner(request.user)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "The user does not exist")
        return redirect('user_list', club_id)
    else:
        if(current_user != user and user.is_active):
            if(is_part_of and is_owner):
                user_memberships = Membership.objects.all().filter(user=user, club=current_club)
                if user_memberships.count() == 1:
                    user_memberships.update(level = '3')
                    user_memberships[0].save()
                    messages.add_message(request, messages.SUCCESS, "Member promoted successfully!")
                    return redirect('user_list', club_id)
                else:
                    return redirect('profile')
            messages.add_message(request, messages.ERROR, "You must be the owner of this club promote members")
            return redirect('profile')
        else:
            messages.add_message(request, messages.ERROR, "You cannot promote yourself or an inactive user!")
            return redirect('user_list', club_id)


@login_required
def demote_club_officer(request, user_id, club_id):
    try:
        current_club=Club.objects.get(id=club_id)
        current_user = request.user
        user = User.objects.get(id=user_id)
        is_part_of = current_club.is_part_of(user)
        is_owner = current_club.is_owner(request.user)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "The user does not exist")
        return redirect('user_list', club_id)
    else:
        if(current_user != user and user.is_active):
            if(is_part_of and is_owner):
                user_memberships = Membership.objects.all().filter(user=user,club=current_club)
                if user_memberships.count() == 1:
                    user_memberships.update(level = '2')
                    user_memberships[0].save()
                    messages.add_message(request, messages.SUCCESS, "Successfully demoted officer!")
                    return redirect('user_list',club_id)
                else:
                    return redirect('profile')
            messages.add_message(request, messages.ERROR, "You must be this club's owner to demote officers")
            return redirect('profile')
        else:
            messages.add_message(request, messages.ERROR, "You cannot demote yourself or an inactive user!")
            return redirect('user_list',club_id)

@login_required
@officer_or_above_required
def accept_club_applicant(request, user_id, club_id):
    try:
        current_club=Club.objects.get(id=club_id)
        current_user = request.user
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "The user does not exist")
        return redirect('user_list', club_id)
    else:
        if(current_user != user and user.is_active):
            user_memberships = Membership.objects.all().filter(user=user, club=current_club)

            if(len(user_memberships) > 0):
                is_applicant = user_memberships[0].is_applicant()
            else:
                messages.add_message(request, messages.ERROR, "Cannot accept this user")
                return redirect('user_list', club_id)

            if is_applicant:
                if user_memberships.count() == 1:
                    user_memberships.update(level='2')
                    messages.add_message(request, messages.SUCCESS, "Accepted applicant successfully!")
                    return redirect('user_list', club_id)
            else:
                messages.add_message(request, messages.ERROR, "Cannot accept a user that is not an applicant")
                return redirect('user_list', club_id)
        else:
            messages.add_message(request, messages.ERROR, "You cannot accept yourself or an in-active applicant!")
            return redirect('user_list', club_id)


def show_club(request, club_id):
    global current_club
    try:
        current_club=Club.objects.get(id=club_id)
        user = request.user
        can_apply = True
        if(user and user.is_authenticated):
            is_owner=current_club.is_owner(user)
            user_membership = Membership.objects.all().filter(user=user, club=current_club)
            if current_club.is_part_of(user) :
                if len(user_membership) != 0:
                    if user_membership[0].is_removed_user():
                        can_apply = True
                    else:
                        can_apply=False
                else:
                    can_apply = False
                if(user != current_club.owner):
                    user_membership=user_membership[0]
        users=current_club.members.all()
        # How applicants will be displayed e.g. 10 people are currently in the waiting list!
        applicants=[
            applicant
                for applicant in users
                    if Membership.objects.all().filter(user=applicant, club=current_club)[0].is_applicant()
        ]
        # How members will be displayed (including owner, not includes applicants) e.g. This club has 15 members!
        members=list(set(users)-set(applicants))
        members.append(current_club.owner)
        # How masters will be displayed e.g. This club has 6 chess masters!
        masters=[
            master
                for master in members
                    if master.chess_level != '1' and master.chess_level != '2'
        ]
    except ObjectDoesNotExist:
        return redirect(user_list, Club.objects.all()[0].id)
    else:
        if user != None and user.is_authenticated:
            clubs=Club.objects.all()

            your_clubs=[club for club in clubs if club.is_part_of(user)]
            for club in your_clubs:
                membership = Membership.objects.all().filter(user=user, club=club)
                if len(membership) > 0:
                    if membership[0].is_removed_user():
                        your_clubs.remove(club)

            other_clubs=list(set(clubs)-set(your_clubs))

            context = {
                'members':members,
                'applicants':applicants,
                'masters':masters,
                'users':users,
                'is_owner':is_owner,
                'your_clubs':your_clubs,
                'other_clubs':other_clubs,
                'current_club':current_club,
                'user_can_apply': can_apply,
                'user_membership':user_membership,
                'current_user':user
            }
            return render(request, 'show_club.html', context)
        else:
            user_membership = None
            context={
                'members':members,
                'applicants':applicants,
                'masters':masters,
                'users':users,
                'current_club':current_club,
                'user_can_apply': can_apply,
                'user_membership':user_membership,
                'current_user':user
            }
            return render(request, 'show_club.html', context)

def apply(request, club_id):
    try:
        club = Club.objects.get(id=club_id)
        user = request.user
        if(not user.is_authenticated):
            return redirect('sign_up')
        if club.is_part_of(user):
            return render(request, 'show_club.html', {'club': club})
        membership = Membership(
            user = user,
            club = club,
            level = "1"
        )
        membership.save()
        club.members.add(user)
        messages.add_message(request, messages.SUCCESS, "You have applied to this club successfully!")
        return redirect('user_list',club_id)
    except Exception:
        return redirect('home')

@login_required
def create_club(request):
    global current_club
    current_user = request.user
    clubs = Club.objects.all()
    your_clubs=[club for club in clubs if club.is_part_of(current_user)]
    other_clubs=[club for club in clubs if not club.is_part_of(current_user)]
    user_membership=None
    is_owner=False
    if current_club:
        is_owner=current_club.is_owner(current_user)
        user_membership= Membership.objects.all().filter(user=current_user, club=current_club)
    else:
        user_membership=None
    if request.method == 'POST':
        form = CreateClubForm(request.POST)
        if form.is_valid():
            club = form.save()
            owner = request.user
            club.save()
            club.owner = owner
            club.save()
            current_club=club
            messages.add_message(request, messages.SUCCESS, "Congratulations! Created a club successfully!")
            return redirect('user_list', club.pk)
        else:
            messages.add_message(request, messages.ERROR, "Invalid input!")
    else:
        form=CreateClubForm()
    context={
            'form':form,
            'current_club':current_club,
            'is_owner':is_owner,
            'your_clubs':your_clubs,
            'other_clubs':other_clubs,
            'user_membership':user_membership,
            'current_user':current_user
        }
    return render(request, 'create_club.html', context)
