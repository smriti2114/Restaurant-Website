
from django.shortcuts import render
from .forms import BookingForm
from .models import Menu, Booking
import json
from django.http import JsonResponse
from datetime import datetime

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def book(request):
    form = BookingForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form':form}
    return render(request, 'book.html', context)

def bookinglist(request, mydate):
    print("inside bookinglist API", request, mydate)
    o = list(Booking.objects.values())
    for i in o:
        print("date is ", i['date'])
    data = list(Booking.objects.filter(date=mydate[7:]).values())
    print("data is ", data)
    for d in data:
        d['timeslot'] = Booking.TIMESLOT_LIST[d['timeslot']][1]
    x = JsonResponse({'text': data})
    print("x is ", x)
    return x

def reservations(request):
    return render(request, 'reservations.html')

def reservationlist(request):
    print("inside list API")
    data = list(Booking.objects.values())
    for d in data:
        d['timeslot'] = Booking.TIMESLOT_LIST[d['timeslot']][1]
    x = JsonResponse({'text': data})
    print("x is ", x)
    return x

def menu(request):
    menu_data = Menu.objects.all()
    main_data = {"menu": menu_data}
    return render(request, 'menu.html', {"menu": main_data})

def display_menu_item(request, pk=None): 
    if pk: 
        menu_item = Menu.objects.get(pk=pk) 
    else: 
        menu_item = "" 
    return render(request, 'menu_item.html', {"menu_item": menu_item}) 
