import datetime
from django.shortcuts import render, HttpResponse,redirect
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login,logout
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
import math
import random

# Create your views here.
def temp(request):
    return render(request,"home/temp.html", context={})
   
def tos(request):
    return render(request,"home/tos.html", context={})   

def pricing(request):
    return render(request,"home/pricing.html", context={})   

def home(request):
    if request.user.is_authenticated: 
        return redirect('dashboard')
    return render(request,"home/home.html", context={})   
 
def forgot(request):
    if request.user.is_authenticated: 
        return redirect('dashboard')
    return render(request,"home/forgot_pass.html", context={})    

def my_admin(request):
    url=settings.BASE_URL+"/admin"
    response=redirect(url)
    return response

def dashboard(request):
    if request.user.is_authenticated:
        todays_date = datetime.date.today()  
        if request.user.is_superuser:
            return redirect('admin')
        try:
            my_draft=Draft.objects.filter(published=True).values()
        except:
            print('unable to fetch post')
        
        try:
            my_customer=Customer.objects.filter(user=request.user)
        except:
            print('unable to fetch users')
        return render(request,"home/dashboard.html", context={'drafts' : my_draft,'permission':my_customer})    
    return render(request,"home/home.html", context={})    

def SENDMAIL(subject, message, email):
    try:
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        send_mail( subject, message, email_from, recipient_list )
    except:
        return HttpResponse('Unable to send Email')
    
def generate_code(length):
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    code = ""
    for i in range(length) :
        code += digits[math.floor(random.random() * 62)]
    return code

def send_activate_email(user,email):
    myuser=User.objects.get(username=user.email)
    try:
        mycustomer=Customer.objects.get(user=myuser)
    except:
        print('No User Found')
    if not myuser.is_active:
        try:
            myotp=myuser.username + generate_code(60)
            mycustomer.otp_code=myotp
            mycustomer.save()
            url=settings.BASE_URL_EMAIL+'/signup/verify/'+myotp
            email_subject='Account Verification Request In ResourceHub'
            email_message='You need To veriy you email in order to continue to our website\n'+'Activation Link:- '+ url
            SENDMAIL(email_subject,email_message,email)
            return True
        except:
            return False
    
def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')     
    if request.method == 'POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        temp_email=request.POST.get('email')
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')
        acc_type=request.POST.get('acc_type')

        email=temp_email.lower()
        if not pass1==pass2:
            messages.error(request, 'Error - Passwords do not match')
            return redirect('signup')
        
        try:
            User.objects.get(email=email)
            messages.error(request, 'Error - Email Already exists.')
            return redirect('signup')
        except:
            pass
        
        try:
            my_type=userType.objects.get(code=acc_type)
        except:
            messages.error(request, 'Error - Account Type was Not found.')
            return redirect('signup')

        myuser=User.objects.create_user(username=email,first_name=first_name,last_name=last_name,
                                        email=email)
        myuser.is_active=False
        myuser.set_password(pass1)
        myuser.save()
        fullname_temp=str(first_name+last_name)
        try:
            Customer.objects.create(user=myuser,is_verified=False,user_Type=my_type,
                                    full_name=fullname_temp,temp_email=email)
        except Exception as e:
            User.objects.get(id=myuser.id).delete()
            return HttpResponse(str(e))

        if send_activate_email(myuser,email):
            messages.error(request, 'Success - Verification link has been sent to your email. So Check You email and verify Your email')
            return redirect('home')
        else:
            messages.error(request, 'Error - Unable to send Notification. But your Account has been created but you will not be able to login as it is inactive so signin to resend link')
            return redirect('home')
        
    return render(request,"home/signup.html", context={})

def activate_by_email(request,code):
    try:
        profile=Customer.objects.get(otp_code=code)
    except:
        print('User Not Found')
    if profile.user.is_active:
        return render(request,'home/email.html')
    myuser=profile.user
    myuser.is_active=True
    myuser.save()
    email=myuser.email
    try:
        email_message='Account Verified In ResourceHub'
        email_subject='Your Account at ResourceHub has been created Verified Visit our page to avail amazing experience'
        SENDMAIL(email_message,email_subject,email)
    except Exception as e:
        print("Can't send email\n", str(e))

    return render(request,'home/email.html')

def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.user.is_authenticated:
        return redirect('dashboard') 

    if request.method == 'POST':
        temp_email=request.POST.get('email')
        password=request.POST.get('pass1')
        
        email=temp_email.lower()
            
        # resend code
        try:
            verify_user=User.objects.get(username=email)    
        except:
            try:
                verify_user=User.objects.get(email=email)    
            except:
                messages.error(request, 'Error - No User found!')
                return redirect('signin')  
        if verify_user.is_active == False:
            if send_activate_email(verify_user,verify_user.email):
                messages.error(request, 'Your Email is not yet verified. So we have Sent Link to your email ,verify that to continue')
                return redirect('home')  
        try:
            tempuser=User.objects.get(email=email).username                  
            user=authenticate(request,username=tempuser,password=password)
        except:
            try:
                User.objects.get(username=email)
                
                user=authenticate(request,username=email,password=password)
                
            except:    
                messages.error(request, 'Error - Entered Username or Email is Not in our records.')
                return redirect('signin')
                  
        if user == None: 
            messages.error(request, 'Error - No User Exists.')
            return redirect('signin')
        
        if user.is_active:
            login(request,user)
            return redirect('dashboard')
        
        else:
            messages.error(request, 'Error - You dont have permission to login.')
            return redirect('signin')
        
    else:
        return render(request,"home/signin.html")
    
def send_forgot_email(user,email):
    myuser=User.objects.get(username=user.username)
    try:
        mycustomer=Customer.objects.get(user=myuser)
    except:
        try:
            mycustomer=Customer.objects.get(user=myuser)
        except:
            print('no User')
            
    if myuser.is_active:
        try:
            myotp=myuser.username + generate_code(60)
            mycustomer.otp_code=myotp
            mycustomer.save()
            url=settings.BASE_URL_EMAIL+'/change/password/'+myotp
            email_subject='Password Changing Request In Resource Hub'
            email_message='Click this link  to Change Your Password.\n'+'Link:- '+ url
            SENDMAIL(email_subject,email_message,email)
            return True
        except:
            return False

def forgot_pass(request):
    if request.method=='POST':
        temp_email=request.POST.get('email')
        
        email=temp_email.lower()
        myuser=User.objects.get(email=email)
        if send_forgot_email(myuser,email):
            messages.error(request, 'Success - Your Request for Forgot Password has been approved, You can Check your Email.')
            return redirect('home')
        else:
            messages.error(request, 'Error - Server Error')
            return redirect('home')
        
def activate_forgot_by_email(request,code):
    try:
        profile=Customer.objects.get(otp_code=code)
        
    except:
        try:
            profile=Customer.objects.get(otp_code=code)
        except:
            messages.error(request, 'Error - User Not Found Signin to get link again')
            return redirect('home')
    myuser=profile.user
    return render(request,'home/changepassword.html',context={"data":myuser})

def create_post(request):
    if request.user.is_authenticated: 
        if request.method=="POST":
            my_title=request.POST.get('title')
            my_subtitle=request.POST.get('subtitle')
            my_description=request.POST.get('description')

            todays_date = datetime.date.today()  
            try:
                myuser=Customer.objects.get(user=request.user)                
            except:
                messages.error(request, 'Error - User Not Found')
                return redirect('dashboard')

            try:
                Draft.objects.create(user=request.user,title=my_title,subtitle=my_subtitle,description=my_description,pub_date=todays_date,published=True)
                messages.error(request, 'Draft Created Successfully')
                return redirect('dashboard')
            except:
                messages.error(request, 'Error - There was an error while creating the draft.')
                return redirect('dashboard')

        return render(request,"home/create_post.html", context={})   
    return render(request,"home/home.html", context={})   

def answer_of_post(request):
    if request.user.is_authenticated: 
        if request.method=="POST":
            que_id=request.POST.get('Unique_id_answer')
            answer_post=request.POST.get('send_ans')

            try:
                my_post=Draft.objects.get(pk=que_id)
            except:
                messages.error(request, 'Error - There was an error while fetching the Question.')
                return redirect('dashboard')
            try:
                review.objects.create(this_draft=my_post,this_user=request.user,reply=answer_post)
                messages.success(request, 'Answer posted Successfully.')
                return redirect('dashboard')
            except:
                messages.error(request, 'Error - There was an error while Answering the Question.')
                return redirect('dashboard')
        return redirect('render_answer_post')
    return render(request,"home/dashboard.html", context={})   

def render_answer_post(request,que_id):
    if request.user.is_authenticated: 
        if request.method=="POST":
            que_id=request.POST.get('Unique_id_answer')
            answer_post=request.POST.get('send_ans')

            try:
                my_post=Draft.objects.get(pk=que_id)
            except:
                messages.error(request, 'Error - There was an error while fetching the Question.')
                return redirect('dashboard')
            try:
                review.objects.create(this_draft=my_post,this_user=request.user,reply=answer_post)
                messages.success(request, 'Answer posted Successfully.')
                return redirect('dashboard')
            except:
                messages.error(request, 'Error - There was an error while Answering the Question.')
                return redirect('dashboard')
        my_post = Draft.objects.filter(pk=que_id)
        return render(request,"home/answer_post.html", context={"thispost":my_post})   
    return render(request,"home/dashboard.html", context={})   

def view_full_que(request,que_id):
    if request.user.is_authenticated: 
        my_post = Draft.objects.filter(pk=que_id)
        my_review = review.objects.filter(this_draft=my_post[0])
        return render(request,"home/view_fullque.html", context={"thispost":my_post,"thisreview":my_review})
    return render(request,"home/home.html", context={})   

def view_volunteers(request):
    if request.user.is_authenticated: 
        try:
            volunteer_type = userType.objects.get(code=settings.USER_VOLUNTEER_CODE)
        except:
            print('Unable to fetch volunteers')
        all_volunteers = Customer.objects.filter(user_Type=volunteer_type).values()
        return render(request,"home/view_allvolunteers.html", context={"volunteer":all_volunteers})   
    return render(request,"home/home.html", context={})   

def view_profile(request):
    if request.user.is_authenticated: 
        if request.method=="POST":
            full_name=request.POST.get('full_name')
            temp_email=request.POST.get('email')
            this_age=request.POST.get('age')
            this_college=request.POST.get('college')
            this_skills=request.POST.get('skills')
            this_experience=request.POST.get('experience')
            old_pass=request.POST.get('old_pass')
            new_pass=request.POST.get('new_pass')
            cnew_pass=request.POST.get('cnew_pass')
            check_passchange=request.POST.get('check_pass')

            verify_email=False   #check to send email
            email=temp_email.lower()
            if email == request.user.email:
                pass
            else:
                verify_email=True 

            name=full_name.split("  ")

            try:
                myuser=User.objects.get(email=request.user.email)
                profile=Customer.objects.get(user=myuser)
            except:
                messages.error(request, 'Error - Internal Error.')
                return redirect('view_profile')
            myuser.username=email
            myuser.first_name=name[0]
            try:
                myuser.last_name=name[1]
            except:
                myuser.last_name=name[0]
            myuser.save()
            profile.full_name=full_name
            profile.temp_email=email
            profile.age=this_age
            profile.college=this_college
            profile.skills=this_skills
            profile.experience=this_experience
            profile.save()
            if verify_email:
                myuser.is_active=False
                myuser.email=email
                myuser.save()
                logout(request)
                if send_activate_email(myuser,email):
                    messages.error(request, 'Success - Verification link has been sent to your email verify that.')
                    return redirect('home')
            elif check_passchange:
                myuser=User.objects.get(email=request.user.email)
                profile=Customer.objects.get(user=myuser)
                try:
                    tempuser=User.objects.get(email=email).username                  
                    user=authenticate(request,username=tempuser,password=password)
                except:
                    try:
                        User.objects.get(username=email)
                        
                        user=authenticate(request,username=email,password=password)
                        
                    except:    
                        messages.error(request, 'Error - Entered Passowrd is incorrect.')
                        return redirect('view_profile')
                if not new_pass==cnew_pass:
                    messages.error(request, 'Error - Passwords do not match')
                    return redirect('view_profile')
                myuser.set_password(new_pass)
                myuser.save()
                messages.error(request, 'Success - Profile Updated Successfully')
                return redirect('view_profile')

            else:
                messages.error(request, 'Success - Profile Update SuccessFully.')
                return redirect('view_profile')
            



        try:
            my_user = Customer.objects.filter(user=request.user)
        except:
            print('Unable to fetch user')
        return render(request,"home/profile.html", context={"this_user":my_user})   
    return render(request,"home/home.html", context={})   