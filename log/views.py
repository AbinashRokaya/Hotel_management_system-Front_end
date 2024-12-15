from crypt import methods
from lib2to3.fixes.fix_input import context
from os import pipe2

from PIL.ImageFile import ERRORS
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import requests
from django.http import JsonResponse, HttpResponse
from dominate.tags import details
from flask import session
from fontTools.misc.cython import returns
from future.backports.http.client import responses
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
import os
from django.conf import settings
from datetime import datetime,timedelta
from django.contrib import messages
from sqlalchemy import false

from .models import Hotel
from thonny.plugins.microbit.api_stubs.microbit import pin10

from thonny.plugins.tomorrow_syntax_theme import tomorrow

# Create your views here.
secret_key = 'django-insecure-l7it*4*z@&2h9mpz7nl!xnrpjc!v*^tk#abcbz6-x_btkwpu5+'
def HomePage(request):
    return render(request,"home.html")

def SignupPage(request):
    if request.method=='POST':
        pas=request.POST.get('password1')
        if len(pas)<=5:
            messages.info(request,'password most be grater than 6 charater!!!')
        data={
            'username':request.POST.get('username'),
            'email':request.POST.get('email'),
            'password':request.POST.get('password1'),
            'password_confirmation':request.POST.get('password2')
        }


        try:
            url = 'http://127.0.0.1:8000/account/register/'
            response = requests.post(url,json=data)


            if response.status_code in [200,201]:
                details=response.json()

                if details['username'][0]=='A user with that username already exists.':
                    messages.info(request,f"{details['username'][0]}")
                if 'error' in details:
                    messages.info(request, f"{details}")




                access_token = details['token']['access']

                # Use .get() to avoid KeyError
                if access_token:
                    request.session['access_token'] = access_token
                    return redirect('guest')

                else:
                    messages.info(request,"not access token")
                    return redirect('register')


                        # Option response = requests.get(myurl, headers={'Aally, set session data or cookies here



            else:
                details = response.json()
                print(details)
                messages.info(request, f"{details['error']}")

        except requests.exceptions.RequestException as e:
            messages.info(request,f"'error': 'An error occurred', 'details':{ str(e)}")



    return render(request,"signup.html")


def LoginPage(request):
    if request.method == 'POST':
        # Collect data from the form
        data = {
            'username': request.POST.get('username'),
            'password': request.POST.get('pass'),

        }

        try:
            # URL of the API endpoint
            url = 'http://127.0.0.1:8000/account/login/'

            # Make the POST request to the API
            response = requests.post(url, json=data)
            # Debugging: Check HTTP status
            # print(response.json())


            # Process the API response
            if response.status_code == 200:  # Assuming 200 is the success status

                response_data=response.json()
                access_token = response_data.get('tokens',{}).get('access')  # Use .get() to avoid KeyError
                if access_token:
                    request.session['access_token'] = access_token
                    return redirect('hotel')

                else:
                    messages.info(request,f"{response_data}")





                # Optionally, set session data or cookies here

            else:
                data_1=response.json()
                messages.info(request,f"{data_1['non_field_errors'][0]}")
                # # return JsonResponse({
                #     "error": "Login failed",
                #     "details": response.json()
                # })

        except  KeyError as e:
            messages.info(request, f"'error': 'An error occurred', 'details':{str(e)}")

    # Render the login form for GET requests
    return render(request, 'login.html')

def LogoutPage(request):
    if request.method=='POST':
        refresh_token=request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
    return redirect('login')

def room(request,id):
    access_token=request.session.get('access_token')
    if not access_token:
        return redirect('login')

    try:

        myurl = 'http://127.0.0.1:8000/room/room_views/'
        response = requests.get(myurl, headers={'Authorization': f'Bearer {access_token}'})
        if request.method == 'POST':
            room_id = request.POST.get('room_id')
            return redirect("reservation", id=room_id)
        if response.status_code==200:
            all_rooms=response.json()
            filter_rooms=[r for r in all_rooms if r['hotel_id']==id]
        else:
            filter_rooms=[]

        return render(request,'room_form.html',{'room':filter_rooms})
    except jwt.ExpiredSignatureError:
        messages.info(request,"Access token has expired.")

        return redirect('login')

    except jwt.InvalidSignatureError:
        messages.info(request,"Invalid token signature.")

        return redirect('login')

    except jwt.InvalidTokenError as e:
        messages.info(request,f"Invalid token: {str(e)}")

        return redirect('login')

def reservation(request,id):
    data={}
    access_token = request.session.get('access_token')
    # print(access_token)
    if not access_token:
        return redirect('login')

    try:
        today_date = datetime.now().strftime("%Y-%m-%d")
        decoded_token = jwt.decode(access_token, secret_key, algorithms=["HS256"])
        user_id = decoded_token.get('user_id')

        if request.method=='POST':

            if request.POST.get('submit')=='submit':
                try:
                    check_out=request.POST.get('out')
                    check_in = request.POST.get('in')


                    #Check the room abiability
                    check_room=f"http://127.0.0.1:8000/room/room_views/{id}/"
                    check_response=requests.get(check_room,headers={'Authorization': f'Bearer {access_token}'})
                    room_details=check_response.json()

                    if not room_details['availability']:
                        messages.info(request,"already booked this toom")
                        return redirect('reservation',id=id)

                    if check_out !="" and check_in!="":
                        try:
                            today = datetime.strptime(check_in, "%d %B, %Y")
                            format_today=today.strftime("%Y-%m-%d")
                            next_day=datetime.strptime(check_out,"%d %B, %Y")
                            format_next = today.strftime("%Y-%m-%d")
                            day=next_day.day-today.day
                        except ValueError as e:
                            messages.info(request,f"{e}")
                            return redirect("reservation",id=id)
                        if day==0:
                            messages.info(request,"You must stay 1 night in hotel.")
                            return redirect('reservation',id=id)
                        else:
                            guest_url = "http://127.0.0.1:8000/guest/guest_views/"
                            guest_res = requests.get(guest_url, headers={'Authorization': f'Bearer {access_token}'})

                            if guest_res.status_code == 200:
                                all_guest = guest_res.json()

                                guest_id = [r for r in all_guest if r['user'] == user_id]
                                for g in guest_id:

                                    data = {
                                        'check_in': f'{format_today}',
                                        'check_out': f'{format_next}',
                                        'status': 'Pending',
                                        'guest_id': g['id'],
                                        'room_id': id
                                    }
                            else:
                                messages.info(request,"guest not found")


                            url='http://127.0.0.1:8000/reservation/reservation_views/'
                            response = requests.post(url,headers={'Authorization': f'Bearer {access_token}'}, json=data)
                            if response.status_code in [201,200]:
                                res = response.json()


                                if 'id' in res:  # Check if 'id' key exists
                                    res_id = res['id']

                                    return redirect('payment', id=res_id, day=day, room=id)
                                else:
                                    messages.info(request, "The reservation response is missing an ID.")
                                    return redirect('reservation', id=id)
                            else:
                                messages.info(request, f"You are not a guest")
                                return redirect('reservation', id=id)
                    else:
                        messages.info(request,"fill the blank !!!")
                        return redirect('reservation',id=id)
            #
            #         next_day=today+timedelta(days=out)

                except requests.exceptions.RequestException as e:


                    return JsonResponse({"error": "An error occurred", "details": str(e)},)
            else:
                return redirect('hotel')

        return render(request,'reservation_form.html',{'today':today_date,'room':id})
    except jwt.ExpiredSignatureError:
        messages.info(request, "Access token has expired.")

        return redirect('login')

    except jwt.InvalidSignatureError:
        messages.info(request, "Invalid token signature.")

        return redirect('login')

    except jwt.InvalidTokenError as e:
        messages.info(request, f"Invalid token: {str(e)}")

        return redirect('login')

def payment(request,id,day,room):
    access_token = request.session.get('access_token')
    if not access_token:
        return redirect('login')

    try:
        today_date = datetime.now().strftime("%Y-%m-%d")
        decoded_token = jwt.decode(access_token, secret_key, algorithms=["HS256"])
        user_id = decoded_token.get('user_id')

        myurl = f'http://127.0.0.1:8000/room/room_views/{room}'
        response = requests.get(myurl, headers={'Authorization': f'Bearer {access_token}'})

        room=response.json()

        room_price=room['price']

        amount=float(room_price)*day


        context={
            "amount":amount
        }
        if request.method=='POST':

            if request.POST.get('submit')=='submit':
                pay=request.POST.get('pay')

                if pay==" ":
                    messages.info(request,"fill the blank !!!")
                    return redirect('payment',id=id,day=day,room=room)

                selection=request.POST.get('selection')
                url="http://127.0.0.1:8000/payment/payment_view/"


                if float(pay)==amount:
                    data={
                        'amount':amount,
                        'method':selection,
                        'status':'Completed',
                        'data':today_date,
                        'reservation_id':id

                    }

                    response = requests.post(url, headers={'Authorization': f'Bearer {access_token}'}, json=data)
                    res = response.json()

                    r_id=room['id']

                    room_url = f"http://127.0.0.1:8000/room/room_views/{r_id}/"
                    room_data = {
                        'room_no':room['room_no'],
                        'price':room['price'],
                        'capacity':room['capacity'],
                        'feature':room['feature'],

                        'availability': False
                    }
                    if response.status_code == 200:

                        room_response = requests.put(room_url, headers={'Authorization': f'Bearer {access_token}'},json=room_data)
                        if room_response.status_code==200:
                            res_url = f"http://127.0.0.1:8000/reservation/reservation_views/{id}/"
                            data = {
                                'status': 'Confirmed'
                            }
                            response_room= requests.put(res_url, headers={'Authorization': f'Bearer {access_token}'},json=data)
                            if response_room.status_code==200:
                                messages.success(request,f"you Successfully book the hotel:{room['hotel_id']} room  no:{room['id']}!!!")
                                return redirect('hotel')
                        else:
                            messages.info(request, "Your payment is not enough!!!")
                else:
                    messages.info(request,"Your payment is not enough!!!")

            else:
                res_url=f"http://127.0.0.1:8000/reservation/reservation_views/{id}/"
                data={
                    'status': 'Cancelled'
                }
                response = requests.put(res_url, headers={'Authorization': f'Bearer {access_token}'}, json=data)

                if response.status_code==200 :
                    return redirect('hotel')
                else:
                    messages.info(request,"something is problem")
        return render(request,"payment_form.html",context)
    except jwt.ExpiredSignatureError:
        messages.info(request, "Access token has expired.")

        return redirect('login')

    except jwt.InvalidSignatureError:
        messages.info(request, "Invalid token signature.")

        return redirect('login')

    except jwt.InvalidTokenError as e:
        messages.info(request, f"Invalid token: {str(e)}")

        return redirect('login')

def hotel(request):

    access_token = request.session.get('access_token')
    if not access_token:
        return redirect('login')

    try:

        myurl = 'http://127.0.0.1:8000/hotel/hotel_views/'

        response = requests.get(myurl, headers={'Authorization': f'Bearer {access_token}'})
        hotel = response.json()
        if request.method=='POST':
            if response.status_code==200:
                hotel_id=request.POST.get('hotel_id')
                return redirect("room",id=hotel_id)
            else:
                return redirect('hotel')

        delete_hotel, _ = Hotel.objects.all().delete()
        for h in hotel:

            hotel_instance= Hotel(name=h['name'],location=h['location'],rating=h['rating'],
                                                 contact=['contact'],
                                                 facilities=h['facilities'])
            hotel_instance.save()

        if request.method=='GET':
            # hotel=Hotel.objects.all().order_by('name')
            hot=request.GET.get('search')
            if hot!=None:
                hotel_1=Hotel.objects.filter(name__icontains=hot).order_by('name')

                # print(hotel_1)
                for hot in hotel_1:
                    # print(hot.name)
                    hotel=[h for h in hotel if h['name']==hot.name]
                # print(hotel)





            # if response.status_code
            #     all_rooms = response.json()
            #     filter_rooms = [r for r in all_rooms if r['hotel_id'] == id]
            # else:
            #     filter_rooms = []



        return render(request, 'hotel_form.html', {'hotel': hotel})

    except jwt.ExpiredSignatureError:
        messages.info(request,"Access token has expired.")

        return redirect('login')

    except jwt.InvalidSignatureError:
        messages.info(request,"Invalid token signature.")

        return redirect('login')

    except jwt.InvalidTokenError as e:
        messages.info(request,f"Invalid token: {str(e)}")

        return redirect('login')

def about(request):
    return  render(request,"about-us.html")

def contact(request):
    return render(request,"contact.html")

def term(request):
    return render(request,"term_of_use.html")

def policy(request):
    return render(request,"Policy.html")

def environment(request):
    return render(request,"environment_policy.html")

def blog(request):
    return render(request,"blog.html")

def guest(request):
    access_token = request.session.get('access_token')

    if not access_token:
        return redirect('login')

    try:

        decoded_token = jwt.decode(access_token, secret_key, algorithms=["HS256"])
        user_id = decoded_token.get('user_id')

        if request.method == 'POST':
            contact=request.POST.get('contact')
            address=request.POST.get('address')
            date_of_birth=request.POST.get('date')

            gender=request.POST.get('gender')

            if len(contact)<10:
                messages.info(request,"number must be 10 digit")
            data={
                'user':user_id,
                'cantact_number':contact,
                'address':address,
                'date_of_birth':date_of_birth,
                'gender':gender

            }
            url="http://127.0.0.1:8000/guest/guest_views/"
            response = requests.post(url, headers={'Authorization': f'Bearer {access_token}'},json=data)

            res=response.json()
            if response.status_code==200:


                    return redirect('hotel')

            else:
                messages.info(request,f"{res}")
                return redirect('guest')










        return render(request, 'guest_form.html')
    except jwt.ExpiredSignatureError:
        messages.info(request, "Access token has expired.")

        return redirect('login')

    except jwt.InvalidSignatureError:
        messages.info(request, "Invalid token signature.")

        return redirect('login')

    except jwt.InvalidTokenError as e:
        messages.info(request, f"Invalid token: {str(e)}")

        return redirect('login')

def porfile(request):
    access_token = request.session.get('access_token')

    if not access_token:
        return redirect('login')

    try:
        context=[]

        decoded_token = jwt.decode(access_token, secret_key, algorithms=["HS256"])
        user_id = decoded_token.get('user_id')

        guest_url='http://127.0.0.1:8000/guest/guest_views/'
        reservation_url='http://127.0.0.1:8000/reservation/reservation_views/'
        room_url='http://127.0.0.1:8000/room/room_views/'
        payment_url='http://127.0.0.1:8000/payment/payment_view/'
        hotel_url='http://127.0.0.1:8000/hotel/hotel_views/'
        guest_res=requests.get(guest_url, headers={'Authorization': f'Bearer {access_token}'})
        guest_data=guest_res.json()

        if guest_res.status_code==200:
            ind_guest = [h for h in guest_data if h['user'] == user_id]

            try:
                reservation_res = requests.get(reservation_url, headers={'Authorization': f'Bearer {access_token}'})
                reservation_data=reservation_res.json()

                if reservation_res.status_code==200:

                    ind_reservation=[r for r in reservation_data if r['guest_id']==ind_guest[0]['id']]
                    try:
                        room_res = requests.get(room_url,headers={'Authorization': f'Bearer {access_token}'})
                        room_data = room_res.json()
                        payment_res = requests.get(payment_url, headers={'Authorization': f'Bearer {access_token}'})
                        payment_data = payment_res.json()
                        # print(payment_data)

                        if room_res.status_code==200 and payment_res.status_code == 200:
                            result_room = []
                            result_payment=[]
                            for re in ind_reservation:



                                result_room.append([ro for ro in room_data if ro['id'] == re['room_id']] )

                                result_payment.append([p for p in payment_data if p['reservation_id']==re['id']] )



                            hotel_res = requests.get(hotel_url, headers={'Authorization': f'Bearer {access_token}'})
                            hotel_data = hotel_res.json()

                            if hotel_res.status_code==200:
                                result_hotel=[]
                                for i in result_room:

                                    result_hotel.append([h for h in hotel_data if h['id']==i[0]['hotel_id']]  )
                                print(len(result_hotel))

                                for i in range(len(result_hotel)):
                                    print(result_hotel[i][0])




                                for i in range(len(ind_reservation)):
                                    if result_hotel[i] and result_room[i] and result_payment[i]:
                                        context.append({
                                            'hotel': result_hotel[i][0]['name'] ,
                                            'room_no': result_room[i][0]['room_no'],
                                            'room_price': result_room[i][0]['price'] ,
                                            'check_in': ind_reservation[i]['check_in'] ,
                                            'check_out': ind_reservation[i]['check_out'] ,
                                            'total': result_payment[i][0]['amount'] ,
                                            'room_status': ind_reservation[i]['status'] ,
                                            'payment_status': result_payment[i][0]['status'],
                                            'reservation_id':ind_reservation[i]['id'],
                                            'room_id': result_room[i][0]['id'],
                                            'format_today':int(ind_reservation[i]['check_out'].split("-")[2])-int(ind_reservation[i]['check_in'].split("-")[2])


                                        })
                                    else:
                                        messages.error(request,
                                                       f"Data missing for reservation {ind_reservation[i]['id']}")







                    except Exception as e:
                        messages.success(request,f"hotel,An error occured: {e}")

            except Exception as e:
                messages.success(request, f"An error occured: {e}")

        # print(context)



        return render(request, "porfile.html",{'context':context})


    except jwt.ExpiredSignatureError:
        messages.info(request, "Access token has expired.")

        return redirect('login')

    except jwt.InvalidSignatureError:
        messages.info(request, "Invalid token signature.")

        return redirect('login')

    except jwt.InvalidTokenError as e:
        messages.info(request, f"Invalid token: {str(e)}")

        return redirect('login')




