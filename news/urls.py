from django.urls import path
from . import views

urlpatterns = [
    path('', views.news, name='news'),
    path('submit/', views.submit, name='submit'),
    path('newest/', views.newest, name='newest'),
    path('<int:submission_id>/', views.submission_details, name='submission_detail'),
<<<<<<< Updated upstream
=======
    path('confirm-delete/<int:comment_id>/', views.confirm_delete, name='confirm_delete'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('from', views.submissions_by_domain, name='submissions_by_domain'),
    path('comment/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('reply/<int:comment_id>/', views.reply_to_comment, name='reply_to_comment')
>>>>>>> Stashed changes
]