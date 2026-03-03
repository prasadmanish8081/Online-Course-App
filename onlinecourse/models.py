from django.conf import settings
from django.db import models


class Instructor(models.Model):
    full_name = models.CharField(max_length=150)
    profile = models.TextField(blank=True)

    def __str__(self):
        return self.full_name


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructors = models.ManyToManyField(Instructor, blank=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)
    content = models.TextField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.course.name} - {self.title}'


class Learner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    occupation = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.user.username


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f'{self.user.username} - {self.course.name}'


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=500)
    grade = models.FloatField(default=1)

    def __str__(self):
        return self.question_text

    def is_get_score(self, selected_choice_ids):
        correct_choice_ids = set(self.choice_set.filter(is_correct=True).values_list('id', flat=True))
        selected_for_question = set(self.choice_set.filter(id__in=selected_choice_ids).values_list('id', flat=True))
        return self.grade if selected_for_question == correct_choice_ids else 0


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)

    def __str__(self):
        return f'Submission {self.id} ({self.enrollment})'
