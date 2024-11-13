from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from news.models import Submission, HiddenSubmission, UpvotedSubmission, \
    Comment, UpvotedComment  # Assuming you have a Submission model in the news app
from .forms import ProfileForm
from .models import Favorite_submission, Favorite_comment
from .utils import calculate_date
from news.utils import calculate_score


def profile(request):
    user_id = request.GET.get('id')
    # `user` es el perfil consultado, mientras que `logged_in_user` es el usuario autenticado
    user = get_object_or_404(User, username=user_id) if user_id else request.user
    if user.is_anonymous:
        return redirect('news:news')
    logged_in_user = request.user  # Usuario autenticado, siempre será el mismo
    account_age = calculate_date(user.date_joined)

    if logged_in_user == user:
        if request.method == 'POST':
            form = ProfileForm(request.POST, instance=user.profile)
            if form.is_valid():
                form.save()
                return redirect('users:profile')
        else:
            form = ProfileForm(instance=user.profile)

        return render(request, 'profile.html', {
            'form': form,
            'user': user,  # El perfil visualizado
            'logged_in_user': logged_in_user, # El usuario autenticado
            'account_age': account_age
        })
    else:
        return render(request, 'profile_public.html', {
            'user': user,
            'logged_in_user': logged_in_user,  # El usuario autenticado
            'account_age': account_age
        })





def submissions(request):
    user_id = request.GET.get('id')
    user = get_object_or_404(User, username=user_id)
    #sort de más reciente a más antiguo
    submissions = Submission.objects.filter(author=user).order_by('-created')

    voted_submissions = []
    if request.user.is_authenticated:
        voted_submissions = UpvotedSubmission.objects.filter(user=request.user).values_list('submission_id', flat=True)

    return render(request, 'submissions.html', {'submissions': submissions, 'username': user.username, 'voted_submissions': voted_submissions})

@login_required
def hidden_submissions(request):
    hidden_submissions_ids = HiddenSubmission.objects.filter(user=request.user).values_list('submission', flat=True)
    submissions = Submission.objects.filter(id__in=hidden_submissions_ids).order_by('-created')

    voted_submissions = UpvotedSubmission.objects.filter(user=request.user).values_list('submission_id', flat=True)
    return render(request, 'hidden.html', {'submissions': submissions, 'voted_submissions': voted_submissions})

@login_required
def unhide_submission(request, submission_id):
    HiddenSubmission.objects.filter(user=request.user, submission_id=submission_id).delete()
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', 'news:news'))
    return HttpResponseRedirect(next_url)

@login_required
def upvote_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)

    if submission.author == request.user:
        return redirect('news:news')

    UpvotedSubmission.objects.create(user=request.user, submission=submission)
    submission.add_point()

    next_url = request.GET.get('next')
    return HttpResponseRedirect(next_url)

@login_required
def upvote_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    UpvotedComment.objects.create(user=request.user, comment=comment)

    next_url = request.GET.get('next')
    return HttpResponseRedirect(next_url)

@login_required
def unvote_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if submission.author == request.user:
        return redirect('news:news')
    UpvotedSubmission.objects.filter(user=request.user, submission=submission).delete()
    submission.subtract_point()

    next_url = request.GET.get('next')
    return HttpResponseRedirect(next_url)

@login_required
def unvote_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    UpvotedComment.objects.filter(user=request.user, comment=comment).delete()

    next_url = request.GET.get('next')
    return HttpResponseRedirect(next_url)

@login_required
def upvoted_submissions(request):
    voted_submissions_ids = UpvotedSubmission.objects.filter(user=request.user).values_list('submission_id', flat=True)
    submissions = Submission.objects.filter(id__in=voted_submissions_ids).order_by('created')

    return render(request, 'upvoted.html', {'submissions': submissions})

@login_required
def upvoted_comments(request):
    voted_comments_ids = UpvotedComment.objects.filter(user=request.user).values_list('comment_id', flat=True)
    comments = Comment.objects.filter(id__in=voted_comments_ids)
    return render(request, 'upvoted_comments.html', {'comments': comments})

@login_required
def add_favorite_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    Favorite_submission.objects.create(user=request.user, submission=submission)
    return redirect(reverse('users:favorites') + '?id=' + str(request.user.id))

@login_required
def add_favorite_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    Favorite_comment.objects.create(user=request.user, comment=comment)
    return redirect(reverse('users:favorites') + '?id=' + str(request.user.id) + '?comments=true')

@login_required
def remove_favorite_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    Favorite_submission.objects.filter(user=request.user, submission=submission).delete()
    return redirect(reverse('users:favorites') + '?id=' + str(request.user.id))

@login_required
def remove_favorite_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    Favorite_comment.objects.filter(user=request.user, comment=comment).delete()
    return redirect(reverse('users:favorites') + '?id=' + str(request.user.id) + '?comments=true')

def favorites(request):
    user_id = request.GET.get('id')
    comments = request.GET.get('comments')
    target_user = get_object_or_404(User, id=user_id)

    voted = []
    req_favorites = []

    if comments == 'true':
        if request.user.is_authenticated:
            # TODO: Falta model de votos en comentarios
            voted = UpvotedComment.objects.filter(user=request.user).values_list('comment_id', flat=True)
            req_favorites = Favorite_comment.objects.filter(user=request.user).values_list('comment_id', flat=True)

        users_favorites = Favorite_comment.objects.filter(user=target_user).values_list('comment_id', flat=True)
        fav_comments = Comment.objects.filter(id__in=users_favorites)
        return render(request, 'favorite_submissions.html', {'comments': fav_comments, 'target_user' : target_user, 'req_favorites' : req_favorites,'voted_comments' : voted,'isComments' : True})
    else:
        if request.user.is_authenticated:
            voted = UpvotedSubmission.objects.filter(user=request.user).values_list('submission_id', flat=True)
            req_favorites = Favorite_submission.objects.filter(user=request.user).values_list('submission_id', flat=True)

        users_favorites = Favorite_submission.objects.filter(user=target_user).values_list('submission_id', flat=True)
        fav_submissions = Submission.objects.filter(id__in=users_favorites)
        return render(request, 'favorite_submissions.html', {'submissions': fav_submissions, 'target_user' : target_user, 'req_favorites' : req_favorites,'voted_submissions' : voted, 'isComments' : False})

def user_comments(request, username):
    print(f"Username recibido: {username}")
    user = get_object_or_404(User, username=username)
    comments = Comment.objects.filter(author=user)
    return render(request, 'user_comments.html', {'comments': comments, 'user': user})