
#from django.contrib import admin
from django.urls import include,path
from pharmacy import views as pharmacy_views

urlpatterns = [
    path('', pharmacy_views.login, name='login'),
    path('login/', pharmacy_views.login, name='login_page'),
    path('logout/', pharmacy_views.logout, name='logout'),
    path('home/', pharmacy_views.home, name='home'),
    #----------------app urls------------------
    path('pharmacy/', include('pharmacy.urls')),
    
]
