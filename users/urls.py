from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.profile, name='profile'),
    path('submissions/', views.submissions, name='submissions'),
    path('hidden/', views.hidden_submissions, name='hidden_submissions'),
    path('unhide/<int:submission_id>/', views.unhide_submission, name='unhide_submission'),
    path('upvote/submission/<int:submission_id>/', views.upvote_submission, name='upvote_submission'),
    path('upvote/comment/<int:comment_id>/', views.upvote_comment, name='upvote_comment'),
    path('unvote/submission/<int:submission_id>/', views.unvote_submission, name='unvote_submission'),
    path('unvote/comment/<int:comment_id>/', views.unvote_comment, name='unvote_comment'),
    path('upvoted/', views.upvoted_submissions, name='voted_submissions'),
    path('upvoted_comments/', views.upvoted_comments, name='voted_comments'),
    path('favorites/', views.favorites, name='favorites'),
    path('favorite/submission/<int:submission_id>', views.add_favorite_submission, name='add_favorite_submission'),
    path('favorite/comment/<int:comment_id>', views.add_favorite_comment, name='add_favorite_comment'),
    path('unfavorite/submission/<int:submission_id>', views.remove_favorite_submission, name='remove_favorite_submission'),
    path('unfavorite/comment/<int:comment_id>', views.remove_favorite_comment, name='remove_favorite_comment'),
    path('profile/<str:username>/comments/', views.user_comments, name='user_comments'),
    path('profile/<str:username>/', views.profile, name='profile')

]
