"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from clubs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name='home'),
    path('profile/',views.profile, name='profile'),
    path('users/club_id_<int:club_id>',views.user_list, name='user_list'),
    path('user/club_id_<int:club_id>/user_id_<int:user_id>',views.show_user, name='show_user'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('log_in/', views.log_in, name='log_in'),
    path('log_out/',views.log_out, name = 'log_out'),
    path('password/',views.password, name = 'password'),
    path('leave_club/club_id_<int:club_id>',views.leave_club, name = 'leave_club'),
    path('delete_user/club_id_<int:club_id>/user_id_<int:user_id>',views.delete_user, name = 'delete_user'),
    path('owner_transfer/club_id_<int:club_id>/user_id_<int:user_id>', views.owner_transfer, name='owner_transfer'),
    path('show_club/club_id_<int:club_id>',views.show_club, name = 'show_club'),
    path('apply/club_id_<int:club_id>',views.apply, name = 'apply'),
    path('promote_club_member/club_id_<int:club_id>/user_id_<int:user_id>',views.promote_club_member, name = 'promote_club_member'),
    path('demote_club_officer/club_id_<int:club_id>/user_id_<int:user_id>',views.demote_club_officer, name = 'demote_club_officer'),
    path('accept_club_applicant/club_id_<int:club_id>/user_id_<int:user_id>',views.accept_club_applicant, name = 'accept_club_applicant'),
    path('create_club/', views.create_club, name='create_club'),
    path('reinstate_deleted_user/club_id_<int:club_id>/user_id_<int:user_id>', views.reinstate_deleted_user, name='reinstate_deleted_user'),
]
