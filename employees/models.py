from django.db import models


class Position(models.Model):

    """Positions of the employees."""
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True, blank=True)


class Employee(models.Model):

    """Employees data."""
    date = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    patronymic = models.CharField(max_length=30)
    born = models.DateField()
    is_seller = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, blank=True)

    @property
    def full_name(self,):
        return "%s %s %s" % (self.last_name, self.first_name, self.patronymic)

    @property
    def initials(self,):
        return "%s %s. %s." % (self.last_name, self.first_name[0],
                               self.patronymic[0])

    @property
    def position(self):
        if self.positions.exists():
            return self.positions.last().position.name
        return ''


class EmployeePosition(models.Model):

    """Career."""
    date = models.DateTimeField(auto_now_add=True)
    employee = models.ForeignKey(Employee, related_name='positions')
    position = models.ForeignKey(Position)
    date_begin = models.DateField()
    date_end = models.DateField(blank=True, null=True)
