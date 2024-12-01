from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pictures')
    rating = models.IntegerField(default=0)
    accepted_answers_count = models.IntegerField(default=0)


class Tag(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)

    def __str__(self):
        return self.name

class Question(models.Model):
      subject = models.CharField(max_length=255)
      description = models.TextField()
      user = models.ForeignKey(User, on_delete=models.CASCADE , related_name='questions')
      tags = models.ManyToManyField(Tag)
      created_at = models.DateTimeField(auto_now_add=True)

      def __str__(self):
          return self.subject

class Answer(models.Model):
    content = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE ,related_name='answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name='answers')
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user} commented on {self.question}"

class Vote(models.Model):
    VOTE_TYPE = (
        ('up', 'up'),
        ('down', 'down'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name='votes')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE ,related_name='votes')
    vote = models.IntegerField(choices=VOTE_TYPE)

    class Meta:
        unique_together = ('user', 'answer')

