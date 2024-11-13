from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Submission(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title
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
    class Meta:
        ordering = ['created_at']


class UpvotedSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'submission')


