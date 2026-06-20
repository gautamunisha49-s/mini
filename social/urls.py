from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),


# meeeeee
    
    # Tapaiko Post ko naya paths:
    # path('feed/', views.feed_view, name='feed'),
    path('post/new/', views.create_post_view, name='create_post'),
    path('post/<int:post_id>/edit/', views.edit_post_view, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post_view, name='delete_post'),

    path('post/<int:post_id>/like/', views.like_post_view, name='like_post'),
    path('post/<int:post_id>/comment/', views.comment_post_view, name='comment_post'), 
    path('comment/<int:comment_id>/delete/', views.delete_comment_view, name='delete_comment'),
    path('notifications/',views.notifications_view, name='notifications'),


# my parttttt

    path(
        'profile/<int:user_id>/',
        views.profile_view,
        name='profile'
    ),

    path(
        'edit-profile/',
        views.edit_profile,
        name='edit_profile'
    ),

    path(
        'search/',
        views.search_user,
        name='search'
    ),

    path(
        'follow/<int:user_id>/',
        views.follow_user,
        name='follow'
    ),
]
