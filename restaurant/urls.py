from django.urls import path, register_converter
from . import views, converters
from django.conf import settings
from django.conf.urls.static import static


register_converter(converters.DateConverter, 'date')

urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name="about"),
    path('book/', views.book, name="book"),
    path('bookinglist/<str:mydate>', views.bookinglist, name="bookinglist"),
    path('reservations/', views.reservations, name="reservations"),
    path('reservationlist/', views.reservationlist, name="reservationlist"),
    path('menu/', views.menu, name="menu"),
    path('menu_item/<int:pk>/', views.display_menu_item, name="menu_item"),
]