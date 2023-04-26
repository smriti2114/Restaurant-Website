from django.test import TestCase
from restaurant.models import Booking

class TestRestaurantModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        Booking.objects.create(first_name="Smriti",
                               last_name="Sharma",
                               guest_number=5,
                               comment="Please reserve a table",
                               date="2023-12-12",
                               timeslot=1)
        pass

    def setUp(self):
        pass

    def test_timeslot_representation(self):
        query_result = Booking.objects.filter(first_name="Smriti")
        self.assertEqual(len(query_result), 1)
        self.assertEqual(query_result[0].time, Booking.TIMESLOT_LIST[1][1])