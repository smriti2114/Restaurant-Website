from rest_framework import serializers
from .models import MenuItem, yourCart, Category, Orderlist, OrderMenuitem, Booking
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class MenuItemSerializer(serializers.ModelSerializer):

    class Meta():
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
        depth = 1


class CategorySerializer(serializers.ModelSerializer):
    class Meta():
        model = Category
        fields = ['slug']


class ManagerListSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['id', 'username', 'email']


class CartHelpSerializer(serializers.ModelSerializer):
    class Meta():
        model = MenuItem
        fields = ['id', 'title', 'price']


class CartSerializer(serializers.ModelSerializer):
    menuitem = CartHelpSerializer()

    class Meta():
        model = yourCart
        fields = ['menuitem', 'quantity', 'price']


class CartAddSerializer(serializers.ModelSerializer):
    class Meta():
        model = yourCart
        fields = ['menuitem', 'quantity']
        extra_kwargs = {
            'quantity': {'min_value': 1},
        }


class CartRemoveSerializer(serializers.ModelSerializer):
    class Meta():
        model = yourCart
        fields = ['menuitem']


class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['username']


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta():
        model = Orderlist
        fields = ['id', 'user', 'total', 'status', 'delivery_staff', 'date']


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta():
        model = Booking
        fields = ['id', 'user', 'guest_number', 'comment', 'date', 'timeslot']


class SingleHelperSerializer(serializers.ModelSerializer):
    class Meta():
        model = MenuItem
        fields = ['title', 'price']


class SingleOrderSerializer(serializers.ModelSerializer):
    menuitem = SingleHelperSerializer()

    class Meta():
        model = OrderMenuitem
        fields = ['menuitem', 'quantity']


class OrderPutSerializer(serializers.ModelSerializer):
    class Meta():
        model = Orderlist
        fields = ['delivery_staff']
