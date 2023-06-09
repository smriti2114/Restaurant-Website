from django.shortcuts import render, get_object_or_404, redirect
from .forms import BookingForm, UserRegisterForm
from .models import *
import json
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from rest_framework import generics
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from .serializers import MenuItemSerializer, ManagerListSerializer, CartSerializer, OrderSerializer, CartAddSerializer, CartRemoveSerializer, SingleOrderSerializer, OrderPutSerializer, CategorySerializer
from .paginations import MenuItemListPagination
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User, Group
from .permissions import IsManager, IsDeliveryStaff
import math
from datetime import date
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth import authenticate, login
from crum import get_current_user


def sendEmail(request,
              user=None,
              email=None,
              date=None,
              timeslot=None,
              subject=None,
              body=None,
              display=None):
    if subject:
        mail_subject = subject
    else:
        mail_subject = "Your reservation has been booked"
    if body:
        mail_body = body
    else:
        mail_body = f"You are booked for date {date} and slot {timeslot} PM, we'll be waiting for you."
    email = EmailMessage(mail_subject, mail_body, to=[email])

    if email.send():
        print("......... Sending email")
        if display:
            messages.success(request, display)
        else:
            messages.success(request,
                             f'Dear {user}, your reservation has been booked successfully.')
    else:
        messages.error("Failed to send an email to " + email)


########### register here #####################################
def register(request):
    print("register was called")
    if request.method == 'POST':
        print("it's a registeration post request")
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            ######################### mail system ####################################
            htmly = get_template('email.html')
            d = {'username': username}
            subject = 'welcome'
            html_content = htmly.render(d)
            msg = sendEmail(request,
                            subject=subject, body=html_content, email=email,
                            display=f'Your account has been created ! You are now able to log in')
            ##################################################################
            return redirect('login')
        else:
            print("Form is not valid ", form.error_messages, form.errors)
    else:
        print("it's a register get request")
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form, 'title': 'register here'})

################ login forms###################################################


def restaurant_login(request):
    if request.method == 'POST':

        # AuthenticationForm_can_also_be_used__

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            form = login(request, user)
            messages.success(request, f' welcome {username} !!')
            return redirect('home')
        else:
            messages.info(request, f'account done not exit plz sign in')
    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'title': 'log in'})


def home(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def book(request):
    print("inside booking ", request.user.is_authenticated, request.user.username)

    form = BookingForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        # import pdb
        # pdb.set_trace()
        if form.is_valid():
            data = list(Booking.objects.filter(
                date=form.cleaned_data['date'], timeslot=form.cleaned_data['timeslot']))
            if data:
                messages.error(
                    request, "An existing timeslot clashes with the given one!")
            else:
                form.save()
                user = get_current_user()
                sendEmail(
                    request, user.first_name +
                    " " + user.last_name,
                    user.email,
                    form.cleaned_data['date'],
                    Booking.TIMESLOT_LIST[form.cleaned_data['timeslot']][1])
        else:
            print("form is not valid ", form.errors)

    context = {'form': form}
    return render(request, 'book.html', context)


def bookinglist(request, mydate):
    user = get_current_user()
    data = list(Booking.objects.filter(user__pk=user.pk, date=mydate[7:]))
    import pdb
    # pdb.set_trace()
    l = []
    for d in data:
        l.append({
            'name': d.user.first_name + " " + d.user.last_name,
            'username': d.user.username,
            'date': d.date,
            'd.timeslot': Booking.TIMESLOT_LIST[d.timeslot][1]
        })
    x = JsonResponse({'text': l})
    return x


def reservations(request):
    return render(request, 'reservations.html')


def reservationlist(request):
    user = get_current_user()
    print("user pk is ", user.pk)
    data = list(Booking.objects.filter(user__pk=user.pk))
    import pdb
    # pdb.set_trace()
    l = []
    for d in data:
        l.append({
            'name': d.user.first_name + " " + d.user.last_name,
            'username': d.user.username,
            'date': d.date,
            'd.timeslot': Booking.TIMESLOT_LIST[d.timeslot][1]
        })

    x = JsonResponse({'text': l})
    print("x is ", x)
    return x


def menu(request):
    menu_data = MenuItem.objects.all()
    main_data = {"menu": menu_data}
    print("returning following data ", main_data)
    return render(request, 'menu.html', {"menu": main_data})


def display_menu_item(request, pk=None):
    if pk:
        menu_item = Menu.objects.get(pk=pk)
    else:
        menu_item = ""
    return render(request, 'menu_item.html', {"menu_item": menu_item})


class MenuItemListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ['title', 'category__title']
    ordering_fields = ['price', 'category']
    pagination_class = MenuItemListPagination

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]


class AuthCategory(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdminUser]


class ViewMenuItem(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get(self, request, pk=None):
        print("ViewMenuItem was called ", pk)
        if pk:
            menu_item = MenuItem.objects.get(pk=pk)
        else:
            menu_item = ""
        return render(request, 'menu_item.html', {"menu_item": menu_item})

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == 'PATCH':
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        if self.request.method == "DELETE":
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def patch(self, request, *args, **kwargs):
        menuitem = MenuItem.objects.get(pk=self.kwargs['pk'])
        menuitem.featured = not menuitem.featured
        menuitem.save()
        return JsonResponse(status=200, data={'message': 'Featured status of {} changed to {}'.format(str(menuitem.title), str(menuitem.featured))})


class ManagerViewlists(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name='Managers')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Managers')
            managers.user_set.add(user)
            return JsonResponse(status=201, data={'message': 'User added to Managers group'})


class ManagerAuthRemove(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    queryset = User.objects.filter(groups__name='Managers')

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        managers = Group.objects.get(name='Managers')
        managers.user_set.remove(user)
        return JsonResponse(status=200, data={'message': 'User removed From Managers group'})


class DeliveryStaffViewList(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name='DeliveryStaff')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            crew = Group.objects.get(name='DeliveryStaff')
            crew.user_set.add(user)
            return JsonResponse(status=201, data={'message': 'User added to Delivery Staff group'})


class DeliveryStaffRemove(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    queryset = User.objects.filter(groups__name='DeliveryStaff')

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        managers = Group.objects.get(name='DeliverySatff')
        managers.user_set.remove(user)
        return JsonResponse(status=201, data={'message': 'User removed from Delivery Staff group'})


class CartViewOperations(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        cart = yourCart.objects.filter(user=self.request.user)
        return cart

    def post(self, request, *arg, **kwargs):
        serialized_item = CartAddSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        id = request.data['menuitem']
        quantity = request.data['quantity']
        item = get_object_or_404(MenuItem, id=id)
        price = int(quantity) * item.price
        try:
            yourCart.objects.create(user=request.user, quantity=quantity,
                                    unit_price=item.price, price=price, menuitem_id=id)
        except:
            return JsonResponse(status=409, data={'message': 'Item is in cart'})
        return JsonResponse(status=201, data={'message': 'Item added to cart!'})

    def delete(self, request, *arg, **kwargs):
        if request.data['menuitem']:
            serialized_item = CartRemoveSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            menuitem = request.data['menuitem']
            cart = get_object_or_404(
                yourCart, user=request.user, menuitem=menuitem)
            cart.delete()
            return JsonResponse(status=200, data={'message': 'Item removed from cart'})
        else:
            yourCart.objects.filter(user=request.user).delete()
            return JsonResponse(status=201, data={'message': 'All Items removed from cart'})


class OrderViewOperations(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderSerializer

    def get_queryset(self, *args, **kwargs):
        print("Get was called for " + str(self.request.user.username))
        if self.request.user.groups.filter(name='Managers').exists() or self.request.user.is_superuser == True:
            query = Orderlist.objects.all()
        elif self.request.user.groups.filter(name='Delivery Staff').exists():
            query = Orderlist.objects.filter(delivery_staff=self.request.user)
        else:
            query = Orderlist.objects.filter(user=self.request.user)
        return query

    def get_permissions(self):
        print("Get permission was called " + self.request.user.username)

        if self.request.method == 'GET' or 'POST':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]

    def post(self, request, *args, **kwargs):
        cart = yourCart.objects.filter(user=request.user)
        x = cart.values_list()
        if len(x) == 0:
            return HttpResponseBadRequest()
        total = math.fsum([float(x[-1]) for x in x])
        order = Orderlist.objects.create(
            user=request.user, status=False, total=total, date=date.today())
        for i in cart.values():
            menuitem = get_object_or_404(MenuItem, id=i['menuitem_id'])
            orderitem = OrderMenuitem.objects.create(
                order=order, menuitem=menuitem, quantity=i['quantity'])
            orderitem.save()
        cart.delete()
        return JsonResponse(status=201, data={'message': 'Your order has been placed! Your order number is {}'.format(str(order.id))})


class ViewSingleOrder(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = SingleOrderSerializer

    def get_permissions(self):
        order = Orderlist.objects.get(pk=self.kwargs['pk'])
        if self.request.user == order.user and self.request.method == 'GET':
            permission_classes = [IsAuthenticated]
        elif self.request.method == 'PUT' or self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        else:
            permission_classes = [IsAuthenticated,
                                  IsDeliveryStaff | IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self, *args, **kwargs):
        query = OrderMenuitem.objects.filter(order_id=self.kwargs['pk'])
        return query

    def patch(self, request, *args, **kwargs):
        order = Orderlist.objects.get(pk=self.kwargs['pk'])
        order.status = not order.status
        order.save()
        return JsonResponse(status=200, data={'message': 'Status of order #' + str(order.id)+' changed to '+str(order.status)})

    def put(self, request, *args, **kwargs):
        serialized_item = OrderPutSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        order_pk = self.kwargs['pk']
        crew_pk = request.data['delivery_crew']
        order = get_object_or_404(Orderlist, pk=order_pk)
        crew = get_object_or_404(User, pk=crew_pk)
        order.delivery_crew = crew
        order.save()
        return JsonResponse(status=201, data={'message': str(crew.username)+' was assigned to order #'+str(order.id)})

    def delete(self, request, *args, **kwargs):
        order = Orderlist.objects.get(pk=self.kwargs['pk'])
        order_number = str(order.id)
        order.delete()
        return JsonResponse(status=200, data={'message': 'Order #{} was deleted'.format(order_number)})
