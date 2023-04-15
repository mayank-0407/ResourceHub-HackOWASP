from django.db import models
from django.contrib.auth.models import User

# Create your models here.
   
class plan(models.Model):

    planname=models.CharField(max_length=20,null=True, blank=True)
    price=models.FloatField(null=True, blank=True)
    description=models.TextField(null=True, blank=True)

    def __str__(self):
        return self.planname
    
class userType(models.Model):

    code=models.IntegerField(null=True,blank=True)
    name=models.CharField(max_length=20,null=True,blank=True)

    def __str__(self):
        return self.name

class Customer(models.Model):

    full_name=models.CharField(max_length=100,null=True,blank=True)
    temp_email=models.CharField(max_length=100,null=True,blank=True)
    user=models.ForeignKey(User, on_delete= models.CASCADE ,null=True, blank=True)
    user_Type=models.ForeignKey(userType,on_delete=models.CASCADE,null=True, blank=True)
    myplan=models.ForeignKey(plan,on_delete= models.CASCADE,null=True, blank=True)
    is_verified=models.BooleanField(default=False,null=True,blank=True)
    age=models.IntegerField(null=True,blank=True)
    college=models.CharField(max_length=100,null=True,blank=True)
    skills=models.CharField(max_length=100,null=True,blank=True)
    experience=models.CharField(max_length=200,null=True,blank=True)
    otp_code=models.CharField(max_length=100,null=True)

    def __str__(self):
        return self.user.username
    
class Draft(models.Model):

    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    title=models.TextField(max_length=40000,null=True)
    subtitle=models.TextField(max_length=3000,null=True,blank=True)
    description=models.TextField(max_length=80000,null=True,blank=True)
    pub_date=models.DateField(null=True,blank=True)
    published=models.BooleanField(default=False,null=True,blank=True)

    def __str__(self):
        return str(self.title)+str('--')+str(self.pub_date)
    
class review(models.Model):

    this_draft=models.ForeignKey(Draft, on_delete=models.CASCADE,null=True,blank=True)
    this_user=models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    reply=models.TextField(max_length=300,blank=True, null=True)

    def __str__(self):
        return self.this_user.username + str('- replied - ')