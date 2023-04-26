import datetime
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

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
      queryset = self._meta.default_manager.filter(timeslot=self.timeslot, date=self.date)
      if self.pk:
         queryset = queryset.exclude(pk=self.pk) # Exclude this object if it is already saved to the database
      if queryset.exists():
         print("Error was raised")
         raise ValidationError('An existing timeslot clashes with the given one!')
      

class Menu(models.Model):
   name = models.CharField(max_length=200) 
   price = models.IntegerField(null=False)
   menu_item_description = models.TextField(max_length=1000, default='') 

   def display_menu_item(request, pk=None): 
      if pk: 
         menu_item = Menu.objects.get(pk=pk) 
      else: 
         menu_item = "" 
      return render(request, 'menu_item.html', {"menu_item": menu_item}) 

   def __str__(self):
      return self.name


      




