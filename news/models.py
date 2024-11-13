from django.db import models
from django.contrib.auth.models import User

from news.utils import get_domain


class Submission(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    domain = models.CharField(max_length=255, null=True)
    text = models.TextField(blank=True, null=True)
    point = models.IntegerField(default=1)
    comment_count = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.url:
            self.domain = get_domain(self.url)

        if self._state.adding:
            self.author.profile.addKarma(1)
        super().save(*args, **kwargs)

    def add_point(self):
        self.point += 1
        self.author.profile.addKarma(1)
        self.save()

    def subtract_point(self):
        if self.point > 0:
            self.point -= 1
            self.author.profile.reduceKarma(1)
            self.save()

class Submission_URL(Submission):
    pass

class Submission_ASK(Submission):
    pass

class HiddenSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return f"/news/{self.id}"
    
class Comment(models.Model):
    submission = models.ForeignKey(Submission, related_name='comments', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    level = models.IntegerField(default=0)
    
    def __str__(self):
        return "self.text"

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.submission.comment_count += 1
            self.submission.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.submission.comment_count -= 1
        self.submission.save()
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['created_at']


class UpvotedSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'submission')

class UpvotedComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'comment')