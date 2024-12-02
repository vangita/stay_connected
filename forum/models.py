from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures', default='cat.jpg')
    rating = models.IntegerField(default=0)
    accepted_answers_count = models.IntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Tag(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    subject = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    tags = models.ManyToManyField(Tag)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


class Answer(models.Model):
    content = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_accepted:
            Answer.objects.filter(question=self.question, is_accepted=True).update(is_accepted=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} commented on {self.question}"


class Vote(models.Model):
    VOTE_TYPE = (
        ('up', 'up'),
        ('down', 'down'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='votes')
    vote = models.CharField(max_length=4, choices=VOTE_TYPE)

    # class Meta:
    #     unique_together = ('user', 'answer')

