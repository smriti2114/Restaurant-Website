from django.forms import ModelForm
from .models import Booking
from django import forms
from django.utils.timezone import now


class DateInput(forms.DateInput):
    input_type = 'date'

    def get_context(self, name, value, attrs):
        attrs.setdefault('min', now().strftime('%Y-%m-%d'))
        return super().get_context(name, value, attrs)


# Code added for loading form data on the Booking page
class BookingForm(ModelForm):
    class Meta:
        model = Booking
        fields = "__all__"
        widgets = {
            'date': DateInput(),
        }
