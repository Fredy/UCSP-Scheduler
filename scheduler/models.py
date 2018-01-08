from django.db import models

class Career(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name

class CourseType(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=5)

    def __str__(self):
        return "{} ({})".format(self.name, self.code)

class Course(models.Model):
    career = models.ForeignKey(Career, on_delete=models.CASCADE)
    ctype = models.ForeignKey(CourseType, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    credits = models.IntegerField()
    semester = models.IntegerField()
    hours = models.IntegerField()

    def __str__(self):
        return self.name

class Teacher(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)

    def __str__(self):
        return ' '.join([self.first_name, self.last_name])

class Group(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teachers = models.ManyToManyField(Teacher, through='TeacherRole') 
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.code

class TeacherRole(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    istheory = models.BooleanField(default=True)

class Event(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    start = models.TimeField()
    end = models.TimeField()
    weekday = models.SmallIntegerField()
