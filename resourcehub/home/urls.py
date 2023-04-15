from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path('', views.home,name="home"),
    path('temp/', views.temp,name="temp"),
    path('tos/', views.tos,name="tos"),
    path('dashboard/pricing/', views.pricing,name="pricing"),
    path('dashboard/', views.dashboard,name="dashboard"),
    path('admin/', views.my_admin,name="admin"),
    path('signup/', views.signup,name="signup"),
    path('signup/verify/<str:code>',views.activate_by_email,name="activate_email"),
    path('signout/', views.signout,name="signout"),
    path('signin/', views.signin,name="signin"),
    path('forgotpassword/', views.forgot_pass,name="forgotpass"),
    path('change/password/<str:code>/',views.activate_forgot_by_email,name="activate_forgot_pass"),
    path('dashboard/createpost', views.create_post,name="create_post"),
    path('dashboard/answer/post/<str:que_id>', views.render_answer_post,name="render_answer_post"),
    path('dashboard/answer/post/<str:que_id>/review', views.answer_of_post,name="answer_post"),
    path('dashboard/view_fullque/<str:que_id>', views.view_full_que,name="view_full_que"),
    path('dashboard/volunteer/profiles', views.view_volunteers,name="view_volunteer_profiles"),
    path('dashboard/profile', views.view_profile,name="view_profile"),
]