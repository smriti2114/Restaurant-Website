from django.urls import path, register_converter, include
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
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('menu-items', views.MenuItemListView.as_view(), name="menu-items"),
    path('menu-items/category', views.AuthCategory.as_view()),
    path('menu_items/<int:pk>', views.ViewMenuItem.as_view(), name="menu_items_pk"),
    path('groups/managers/users', views.ManagerViewlists.as_view()),
    path('groups/managers/users/<int:pk>', views.ManagerAuthRemove.as_view()),
    path('groups/delivery-staff/users', views.DeliveryStaffViewList.as_view()),
    path('groups/delivery-staff/users/<int:pk>',
         views.DeliveryStaffRemove.as_view()),
    path('cart/menu-items', views.CartViewOperations.as_view()),
    path('orders', views.OrderViewOperations.as_view()),
    path('orders/<int:pk>', views.ViewSingleOrder.as_view()),
]
