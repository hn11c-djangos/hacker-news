from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from users.models import Favorite_comment
from users.utils import calculate_date
from .models import Submission, HiddenSubmission, UpvotedSubmission, Comment, UpvotedComment
from .models import Submission_URL, Submission_ASK
from .forms import SubmissionForm, CommentForm, EditSubmissionForm
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.contrib import messages
from .utils import calculate_account_age
from .utils import calculate_score


def news(request):
    if request.user.is_authenticated:
        hidden_submissions = HiddenSubmission.objects.filter(user=request.user).values_list('submission', flat=True)
        submissions = Submission.objects.exclude(id__in=hidden_submissions)
        voted_submissions = UpvotedSubmission.objects.filter(user=request.user).values_list('submission_id', flat=True)
    else:
        submissions = Submission.objects.all()
        hidden_submissions = []
        voted_submissions = []

    submissions = sorted(submissions, key=calculate_score, reverse=True)

    return render(request, 'news.html', {
        'submissions': submissions,
        'voted_submissions': voted_submissions
    })

@login_required
def submit(request):
    if request.method == "POST":
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission_data = form.save(commit=False)
            submission_data.author = request.user  # Link the submission with the current user
            if submission_data.url:
                Submission_URL.objects.create(
                    title=submission_data.title,
                    url=submission_data.url,
                    text=submission_data.text,
                    author=submission_data.author
                )
            else:
                Submission_ASK.objects.create(
                    title=submission_data.title,
                    text=submission_data.text,
                    author=submission_data.author
                )
            return redirect('news:news')  # Redirect to the main page
        else:
            for error in form.errors.get('url', []):
                if "URL already exists" in error:
                    submission_id = error.split(":")[1]
                    return redirect('news:submission_detail', submission_id=submission_id)

    else:
        form = SubmissionForm()
    return render(request, 'submit.html', {'form': form})

def newest(request):
    voted_submissions = []
    if request.user.is_authenticated:
        hidden_submissions = HiddenSubmission.objects.filter(user=request.user).values_list('submission', flat=True)
        submissions = Submission.objects.exclude(id__in=hidden_submissions).order_by('-created')
        voted_submissions = UpvotedSubmission.objects.filter(user=request.user).values_list('submission_id', flat=True)
    else:
        submissions = Submission.objects.all().order_by('-created')
    return render(request, 'news.html', {'submissions': submissions, 'voted_submissions': voted_submissions})

def ask(request):
    voted_submissions = []
    submissions = Submission_ASK.objects.all()
    if request.user.is_authenticated:
        voted_submissions = UpvotedSubmission.objects.filter(user=request.user).values_list('submission_id', flat=True)

    submissions = sorted(submissions, key=calculate_score, reverse=True)
    return render(request, 'ask.html', {'submissions': submissions, 'voted_submissions': voted_submissions})


def detail(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    return render(request, 'detail.html', {'submission': submission})

@login_required
def hide_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    HiddenSubmission.objects.get_or_create(user=request.user, submission=submission)
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', 'news:news'))
    return HttpResponseRedirect(next_url)

#eliminar submission propia
@login_required
def delete_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if submission.author == request.user:
        submission.delete()
    return redirect('news:news')

#busqueda
def search(request):
    query = request.GET.get('q')
    if query:
        results = Submission.objects.filter(title__icontains=query)
    else:
        results = Submission.objects.none()

    results = sorted(results, key=calculate_score, reverse=True)

    voted_submissions = []
    if request.user.is_authenticated:
        voted_submissions = UpvotedSubmission.objects.filter(user=request.user).values_list('submission_id', flat=True)

    return render(request, 'search_results.html', {'results': results, 'voted_submissions': voted_submissions})


def submission_details(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    comments = Comment.objects.filter(submission=submission, parent__isnull=True)  # Solo comentarios principales

    voted_comments = []
    submissionVoted = False
    if request.user.is_authenticated:
        voted_comments = UpvotedComment.objects.filter(user=request.user).values_list('comment_id', flat=True)
        submissionVoted = UpvotedSubmission.objects.filter(user=request.user, submission=submission).exists()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect('news:submission_detail', submission_id=submission.id)

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.submission = submission
            comment.save()
            return redirect('news:submission_detail', submission_id=submission.id)
    else:
        form = CommentForm()

    return render(request, 'submission_details.html', {
        'submission': submission,
        'comments': comments,
        'form': form,
        'voted_comments': voted_comments,
        'submissionVoted': submissionVoted
    })


@login_required
def confirm_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    submission = comment.submission
    if comment.author != request.user:
        return redirect('news:submission_detail', submission_id=comment.submission.id)

    if request.method == 'POST':
        comment.delete()
        return redirect('news:submission_detail', submission_id=comment.submission.id)

    return render(request, 'confirm_delete.html', {'comment': comment, 'submission': submission})

def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        raise Http404("You are not allowed to delete this comment.")

    comment.delete()
    return redirect('news:submission_detail', submission_id=comment.submission.id)

def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Verificar si el usuario es el autor del comentario
    if comment.author != request.user:
        messages.error(request, "You do not have permission to edit this comment.")
        return redirect('news:submission_detail', submission_id=comment.submission.id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)  # Rellenar el formulario con los datos del comentario
        if form.is_valid():
            form.save()  # Guardar el comentario editado
            return redirect('news:submission_detail', submission_id=comment.submission.id)
    else:
        form = CommentForm(instance=comment)  # Si es un GET, mostrar el formulario con los datos del comentario

    return render(request, 'edit_comment.html', {'form': form, 'comment': comment})

@login_required
def reply_to_comment(request, comment_id):
    reply = request.GET.get('reply')
    is_reply = True if reply == 'true' else False
    original_comment = get_object_or_404(Comment, id=comment_id)
    submission = original_comment.submission
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.submission = submission
            reply.parent = original_comment
            reply.save()
            return redirect('news:submission_detail', submission_id=submission.id)
    else:
        form = CommentForm()

    is_voted = False
    is_favorite = False
    if request.user.is_authenticated:
        is_voted = UpvotedComment.objects.filter(user=request.user, comment=original_comment).exists()
        is_favorite = Favorite_comment.objects.filter(user=request.user, comment=original_comment).exists()
    return render(request, 'reply_to_comment.html', {'form': form, 'original_comment': original_comment, 'is_voted': is_voted, 'is_favorite': is_favorite, 'is_reply': is_reply})

def submissions_by_domain(request):
    domain = request.GET.get('domain')
    submissions = Submission.objects.filter(domain=domain)
    voted_submissions = []
    if request.user.is_authenticated:
        voted_submissions = UpvotedSubmission.objects.filter(user=request.user).values_list('submission_id', flat=True)

    return render(request, 'submissions_by_domain.html', {
        'submissions': submissions,
        'domain': domain,
        'voted_submissions': voted_submissions
    })

def comments(request):
    comments = Comment.objects.all().order_by('-created_at')  # Ordenar por fecha de creación, de más nuevo a más antiguo
    voted_comments = []
    if request.user.is_authenticated:
        voted_comments = UpvotedComment.objects.filter(user=request.user).values_list('comment_id', flat=True)
    return render(request, 'comments.html', {'comments': comments, 'voted_comments': voted_comments})

@login_required
def threads(request):
    comments = Comment.objects.filter(author=request.user,parent__isnull=True).order_by('-created_at')
    voted_comments = []
    if request.user.is_authenticated:
        voted_comments = UpvotedComment.objects.filter(user=request.user).values_list('comment_id', flat=True)
    return render(request, 'threads.html', {'comments': comments, 'voted_comments': voted_comments})

@login_required
def edit_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id, author=request.user)
    if request.method == 'POST':
        form = EditSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Submission updated successfully.')
            return redirect('news:edit_submission', submission_id=submission.id)
    else:
        form = EditSubmissionForm(instance=submission)
    return render(request, 'edit_submission.html', {'form': form, 'submission': submission})