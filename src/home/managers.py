from django.db import models


# class CourseManager(models.Manager):
#     """
#     Course manager
#     Returns:
#         1. Courses with more than 2 videos
#     """
#
#     def get_queryset(self):
#         original_qs = super(CourseManager, self).get_queryset()
#
#         ids = []
#
#         for instance in original_qs:
#             [ids.append(instance.id) if instance.videocourse_set.count() > 1 else None]
#
#         return_qs = original_qs.filter(id__in=ids)
#
#         return return_qs
