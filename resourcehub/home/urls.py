from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path('', views.home,name="home"),
    path('dashboard/', views.dashboard,name="dashboard"),
    path('admin/', views.my_admin,name="admin"),
    path('signup/', views.signup,name="signup"),
    path('signup/verify/<str:code>',views.activate_by_email,name="activate_email"),
    path('signout/', views.signout,name="signout"),
    path('signin/', views.signin,name="signin"),
]