from django.db import models
from django.contrib.auth.models import AbstractUser
#djangonun hazır kullanıcı modeli


class User(AbstractUser):
    """Custom user modeli oluşturduk.Ek alanlar ekleyebiliriz.
    """
    email = models.EmailField(unique = True)#Aynı email ile kayıt olmayı engeller
    #username, password, first_name, last_name, email, last_login, is_staff, is_superuser gibi alanlar AbstractUser dan geliyor.
    #ToString metodu.
    def __str__(self):
        return self.username
