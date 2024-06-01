
#from django.contrib import admin
from django.urls import include,path
from management import views as management_views

urlpatterns = [
    path('', management_views.login, name='login'),
    path('login/', management_views.login, name='login_page'),
    path('logout/', management_views.logout, name='logout'),
    path('home/', management_views.home, name='home'),
    #----------------app urls------------------
    path('pharmacy/', include('pharmacy.urls')),
    
]
