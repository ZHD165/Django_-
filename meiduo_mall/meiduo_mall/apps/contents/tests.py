from django.test import TestCase

# Create your tests here.
import calendar
from datetime import date

mydate = date.today()
result = calendar.calendar(2020)
print(result)