from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Q
from django.urls import reverse
from PIL import Image

# from result.models import TakenCourse
from course.models import Program

from .validators import ASCIIUsernameValidator

# LEVEL_COURSE = "Level course"
BACHLOAR_DEGREE = "Intro"
MASTER_DEGREE = "Middle"

LEVEL = (
    # (LEVEL_COURSE, "Level course"),
    (BACHLOAR_DEGREE, "Intro Degree"),
    (MASTER_DEGREE, "Middle Degree"),
)

FATHER = "Father"
MOTHER = "Mother"
BROTHER = "Brother"
SISTER = "Sister"
GRAND_MOTHER = "Grand mother"
GRAND_FATHER = "Grand father"
OTHER = "Other"

RELATION_SHIP = (
    (FATHER, "Father"),
    (MOTHER, "Mother"),
    (BROTHER, "Brother"),
    (SISTER, "Sister"),
    (GRAND_MOTHER, "Grand mother"),
    (GRAND_FATHER, "Grand father"),
    (OTHER, "Other"),
)


class UserManager(UserManager):

    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(username__icontains=query) |
                         Q(first_name__icontains=query) |
                         Q(last_name__icontains=query) |
                         Q(email__icontains=query)
                        )
            qs = qs.filter(or_lookup).distinct()  # distinct() is often necessary with Q lookups
        return qs


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_dep_head = models.BooleanField(default=False)
    phone = models.CharField(max_length=60, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    picture = models.ImageField(upload_to='profile_pictures/%y/%m/%d/', default='default.png', null=True)
    email = models.EmailField(blank=True, null=True)

    username_validator = ASCIIUsernameValidator()

    objects = UserManager()

    @property
    def get_full_name(self):
        full_name = self.username
        if self.first_name and self.last_name:
            full_name = self.first_name + " " + self.last_name
        return full_name

    def __str__(self):
        return '{} ({})'.format(self.username, self.get_full_name)

    @property
    def get_user_role(self):
        if self.is_superuser:
            return "Admin"
        elif self.is_student:
            return "Student"
        elif self.is_lecturer:
            return "Lecturer"
        elif self.is_parent:
            return "Parent"

    def get_picture(self):
        try:
            return self.picture.url
        except:
            no_picture = settings.MEDIA_URL + 'default.png'
            return no_picture

    def get_absolute_url(self):
        return reverse('profile_single', kwargs={'id': self.id})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.picture.path)
        except:
            pass

    def delete(self, *args, **kwargs):
        if self.picture.url != settings.MEDIA_URL + 'default.png':
            self.picture.delete()
        super().delete(*args, **kwargs)


class StudentManager(models.Manager):

    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(level__icontains=query) |
                         Q(department__icontains=query)
                        )
            qs = qs.filter(or_lookup).distinct()  # distinct() is often necessary with Q lookups
        return qs


class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    # id_number = models.CharField(max_length=20, unique=True, blank=True)
    level = models.CharField(max_length=25, choices=LEVEL, null=True)
    department = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)

    objects = StudentManager()

    def __str__(self):
        return self.student.get_full_name

    def get_absolute_url(self):
        return reverse('profile_single', kwargs={'id': self.id})

    def delete(self, *args, **kwargs):
        self.student.delete()
        super().delete(*args, **kwargs)
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if the Student instance is new.
        super().save(*args, **kwargs)  # Call the "real" save() method.
        if is_new and self.department:  # Check if the student is new and has a department.
            from course.models import Course  # Import Course model here
            from result.models import TakenCourse  # Import TakenCourse model here
            courses = Course.objects.filter(program=self.department)
  # Get all the courses in the department.
            for course in courses:  # Iterate over the courses.
                TakenCourse.objects.create(student=self, course=course)  # Create a TakenCourse instance for each course.


class Parent(models.Model):
    """
    Connect student with their parent, parents can
    only view their connected students information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student = models.OneToOneField(Student, null=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=60, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # What is the relationship between the student and the parent (i.e. father, mother, brother, sister)
    relation_ship = models.TextField(choices=RELATION_SHIP, blank=True)

    def __str__(self):
        return self.user.username


class DepartmentHead(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "{}".format(self.user)
