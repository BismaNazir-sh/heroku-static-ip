from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse, HttpResponseServerError
from django.views.decorators.clickjacking import xframe_options_exempt
from rest_framework import status
import bcrypt
import json
from pharmacy_terminal.globalConfig.mongo_client import *
import re
import bcrypt
from logging import info, error, warning
import requests

# Create your views here.
#==================================================================================================
#----------------------------------------ORDER VIEWS-----------------------------------------------
#==================================================================================================
@xframe_options_exempt
def orders(request):
    username = request.session.get('username')
    role = request.session.get('role')
    if username and ((role == 'pharmacy_admin')or(role == 'super_admin')):
        return render(request, 'orders.html', {'orderStatus': "All"})
    else:
        request.session.flush()
        return redirect('login_page')

# Create your views here.
#==================================================================================================
#----------------------------------------TOP LEVEL VIEWS-------------------------------------------
#==================================================================================================

#---------------------------------------------------------------------------------------------------
def login(request):
    
    if request.method == 'GET':
        return render(request, 'login.html')
    
    if request.method == 'POST':
        info("-------------------------------------------LOGIN--------------------------------------")

        #Get username and password        
        username = request.POST.get('username')
        password = request.POST.get('password')
        username = username.strip()
        username = username.lower()
        # When checking a login
        password_to_check = password.encode('utf-8')  # Convert to bytes
        user = user_collection.find_one({"username": username})
        if user:
            if user: #and bcrypt.checkpw(password_to_check, user["password"]):
                info("Password is correct")
                info("User found")
                
                #Saving session
                request.session['username'] = username
                request.session['role'] = user["role"]
                if('can_reopen_order' in user):
                    request.session['can_reopen_order'] = user["can_reopen_order"]

                if(user["role"] != 'super_admin'):
                    request.session['pharmacy_ncpdpid'] = user["pharmacy_ncpdpid"]
                    temp_pharmacy = pharmacy_collection.find_one({"ncpdpid":user["pharmacy_ncpdpid"]})
                    request.session['integrated_label'] = temp_pharmacy.get('integrated_label', False)
                    if('bulk_fill' in temp_pharmacy):
                        request.session['bulk_fill'] = temp_pharmacy['bulk_fill']
                    
                    if('bulk_ship' in temp_pharmacy):
                        request.session['bulk_ship'] = temp_pharmacy['bulk_ship']

                
                    
                result = {"success": 1, "message": "Login Success","error_code":0}
                return redirect('home')
            else:
                warning("Password is incorrect")
                result = {"success": 0, "message": "Login Failed","error_code":1}
                return render(request, 'login.html',result)

        else:
            warning("User not found")
            result = {"success": 0, "message": "Login Failed","error_code":1}
            return render(request, 'login.html',result)
        
    return redirect('login_page')
#---------------------------------------------------------------------------------------------------
def logout(request):
    username = request.session.get('username')
    if username:
        request.session.flush()
        return redirect('login_page')
    else:
        return redirect('login_page')
#---------------------------------------------------------------------------------------------------
def home(request):
    username = request.session.get('username')
    if username:
        return render(request, 'home.html')
    else:
        request.session.flush()
        return redirect('login_page')
#---------------------------------------------------------------------------------------------------
