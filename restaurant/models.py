import datetime
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages


class Booking(models.Model):
    TIMESLOT_LIST = (
        (0, '02:00 – 02:30'),
        (1, '02:30 – 03:00'),
        (2, '03:00 – 03:30'),
        (3, '03:30 – 04:00'),
        (4, '04:00 – 04:30'),
        (5, '04:30 – 05:00'),
        (6, '05:00 – 05:30'),
        (7, '05:30 – 06:00'),
        (8, '06:30 – 07:00'),
        (9, '07:00 – 07:30'),
        (8, '07:30 – 08:00'),
        (8, '08:00 – 08:30'),
        (8, '08:30 – 09:00'),
    )

    def date_validation(value):
        if value < datetime.date.today():
            raise ValidationError("The date cannot be in the past")
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(
        max_length=254, default="smritisharmatemp@gmail.com")
    guest_number = models.IntegerField()
    comment = models.CharField(max_length=1000)
    date = models.DateField()
    timeslot = models.IntegerField(choices=TIMESLOT_LIST, default=0)\


    def __str__(self):
        return self.first_name + ' ' + self.last_name

    @property
    def time(self):
        return self.TIMESLOT_LIST[self.timeslot][1]

    def clean(self):
        print("clean was called")
        # Queryset that finds all clashing timeslots with the same day
        queryset = self._meta.default_manager.filter(
            timeslot=self.timeslot, date=self.date)
        if self.pk:
            # Exclude this object if it is already saved to the database
            queryset = queryset.exclude(pk=self.pk)
        if queryset.exists():
            return False


class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.title


class yourCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta():
        unique_together = ('menuitem', 'user')

    def __str__(self):
        return self.user


class Orderlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_staff = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="delivery_Staff",
                                       null=True, limit_choices_to={'groups__name': "Delivery crew"})
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True)

    def __str__(self):
        return str(self.id)


class OrderMenuitem(models.Model):
    order = models.ForeignKey(Orderlist, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()

    class Meta():
        unique_together = ('order', 'menuitem')
