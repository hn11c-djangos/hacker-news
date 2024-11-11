from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

from news.models import Submission, HiddenSubmission, UpvotedSubmission  # Assuming you have a Submission model in the news app
from .forms import ProfileForm
from .utils import calculate_account_age


def profile(request):
    user_id = request.GET.get('id')
    # `user` es el perfil consultado, mientras que `logged_in_user` es el usuario autenticado
    user = get_object_or_404(User, username=user_id) if user_id else request.user
    if user.is_anonymous:
        return redirect('news:news')
    logged_in_user = request.user  # Usuario autenticado, siempre será el mismo
    account_age = calculate_account_age(user.date_joined)

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
    submissions = Submission.objects.filter(author=user)
    voted_submissions = []
    if request.user.is_authenticated:
        voted_submissions = UpvotedSubmission.objects.filter(user=request.user).values_list('submission_id', flat=True)

    for submission in submissions:
        submission.created_age = calculate_account_age(submission.created)

    return render(request, 'submissions.html', {'submissions': submissions, 'username': user.username, 'voted_submissions': voted_submissions})

@login_required
def hidden_submissions(request):
    hidden_submissions_ids = HiddenSubmission.objects.filter(user=request.user).values_list('submission', flat=True)
    submissions = Submission.objects.filter(id__in=hidden_submissions_ids)

    for submission in submissions:
        submission.created_age = calculate_account_age(submission.created)

    return render(request, 'hidden.html', {'submissions': submissions, 'username': request.user.username})

@login_required
def unhide_submission(request, submission_id):
    HiddenSubmission.objects.filter(user=request.user, submission_id=submission_id).delete()
    return redirect('users:hidden_submissions')

@login_required
def upvote(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)

    if submission.author == request.user:
        return redirect('news:news')

    UpvotedSubmission.objects.create(user=request.user, submission=submission)
    submission.add_point()
    return redirect('news:news')

@login_required
def unvote(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if submission.author == request.user:
        return redirect('news:news')
    UpvotedSubmission.objects.filter(user=request.user, submission=submission).delete()
    submission.subtract_point()

    next_url = request.GET.get('next')
    return HttpResponseRedirect(next_url)

@login_required
def upvoted_submissions(request):
    voted_submissions_ids = UpvotedSubmission.objects.filter(user=request.user).values_list('submission_id', flat=True)
    submissions = Submission.objects.filter(id__in=voted_submissions_ids)

    for submission in submissions:
        submission.created_age = calculate_account_age(submission.created)

    return render(request, 'upvoted.html', {'submissions': submissions})