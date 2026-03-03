from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .models import Course, Enrollment, Submission


def course_list(request):
    courses = Course.objects.all()
    return render(request, 'onlinecourse/course_list.html', {'courses': courses})


@login_required
@require_http_methods(['GET'])
def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    return render(request, 'onlinecourse/course_details_bootstrap.html', {
        'course': course,
        'enrolled': enrolled,
    })


@login_required
@require_http_methods(['POST'])
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    Enrollment.objects.get_or_create(user=request.user, course=course)
    return HttpResponseRedirect(reverse('onlinecourse:course_detail', args=(course.id,)))


@login_required
@require_http_methods(['POST'])
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    submitted_answer_ids = []
    for key in request.POST:
        if key.startswith('choice'):
            submitted_answer_ids.append(int(request.POST[key]))

    submission = Submission.objects.create(enrollment=enrollment)
    if submitted_answer_ids:
        submission.choices.set(submitted_answer_ids)

    return HttpResponseRedirect(
        reverse('onlinecourse:show_exam_result', args=(course.id, submission.id))
    )


@login_required
@require_http_methods(['GET'])
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id, enrollment__user=request.user)

    selected_choice_ids = set(submission.choices.values_list('id', flat=True))

    total = 0
    possible = 0
    for question in course.question_set.all():
        possible += question.grade
        total += question.is_get_score(selected_choice_ids)

    total_score = total
    possible_score = possible
    grade_percent = round((total_score / possible_score) * 100, 2) if possible_score else 0

    return render(request, 'onlinecourse/exam_result_bootstrap.html', {
        'course': course,
        'submission': submission,
        'selected_choice_ids': selected_choice_ids,
        'total': total,
        'possible': possible,
        'total_score': total_score,
        'possible_score': possible_score,
        'grade_percent': grade_percent,
        'is_passed': grade_percent >= 50,
    })
