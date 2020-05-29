from django.db import models

# Create your models here.
from rest_framework import serializers
from users.models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields=('id','username','mobile','email')