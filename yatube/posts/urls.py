from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('group/<slug:group_list>/', views.GroupPosts.as_view(),
         name='group_list'),
    path('profile/<str:username>/', views.Profile.as_view(), name='profile'),
    path('posts/<int:pk>/', views.PostDetail.as_view(),
         name='post_detail'),
    path('create/', views.PostCreate.as_view(), name='post_create'),
    path('posts/<int:pk>/edit/', views.PostEdit.as_view(),
         name='post_edit'),
    path('posts/<int:pk>/comment/', views.AddComment.as_view(),
         name='add_comment'),
    path('follow/', views.FollowIndex.as_view(), name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.ProfileFollow.as_view(),
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.ProfileUnfollow.as_view(),
        name='profile_unfollow'
    ),
]
