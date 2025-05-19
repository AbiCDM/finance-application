from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
# Create your models here.


TYPE = (
    ('Postive', 'Postive'),
    ('Negavtive' , 'Negavtive')
    )

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    income = models.FloatField()
    expenses = models.FloatField(default=0)
    balance = models.FloatField(blank=True , null=True)
    

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ('user', 'name')  # чтобы у одного пользователя не было дубликатов

    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.FloatField()
    expense_type = models.CharField(max_length=100 , choices=TYPE)
    date = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    


    


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, income=0, expenses=0, balance=0)
    
    def __str__(self):
        return self.name
    