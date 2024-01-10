from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth import login as auth_login
from django import template
from django.db.models import Q
from django.utils.timezone import now
from django.contrib import messages
from .utils import *
from .forms import *


@login_required
def edit_profile(request):
    user = request.user
    form = ProfileForm(instance = user)
    id = request.user.id
    print(user)
    print(id)
    if request.method == 'POST':
        form = ProfileForm(request.POST,request.FILES,instance = user)
        if form.is_valid():
            bio = form.cleaned_data['bio']
            location = form.cleaned_data['location']
            birth_date = form.cleaned_data['birth_date']
            if Profile.objects.filter(user_id = id) is not None:
                prof = Profile.objects.filter(user_id = id)
                prof.delete()
                Profile.objects.create(user_id = id, bio = bio, location = location, birth_date = birth_date)
            else:
                Profile.objects.create(user_id = id, bio = bio, location = location, birth_date = birth_date)
            
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'profileedit.html', {'form': form})

def list(request):
    restourants = Restaurants.objects.all()
    restaurants_with_reviews = []
    for r in restourants:
        reviews = r.review_set.all()
        if reviews:
            rating = average_rating([review.rating for review in reviews])
            number_of_reviews = len(reviews)
        else:
            rating = None
            number_of_reviews = 0
        restaurants_with_reviews.append({"restaurant": r, "rating": rating, "number_of_reviews": number_of_reviews})

    context = {
        "list": restaurants_with_reviews
    }
    return render(request, "list.html", context)

def restaurant_search(request):
    if request.method == 'POST':
        query = request.POST['search']
        print(query)
        if query:
            restaurant = Restaurants.objects.filter(title__icontains = query) 
            context = {
                "list": restaurant
            }
            return render(request, 'restaurant_search.html', context)
        
        return redirect('home')
    else:

        return render(request, 'restaurant_search.html')

def detail_page(request, id):
    obj = get_object_or_404(Restaurants, id = id)
    print(obj)
    menu_res = []
    for food in Menu.objects.filter(restaurant_id = id):
        menu_res.append(food)

    reviews = Review.objects.filter(restaurant_id = id).order_by('-id')[:2]
    
    print(reviews)

    if request.method == 'POST':
        form = ReviewsForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.restaurant = obj
            review.creator_id = request.user.id
            print(review)
            review.save()
    else:
        form = ReviewsForm()
    return render(request, 'detail.html', {'menu' : menu_res , 'obj' : obj, 'form' : form , 'rev' : reviews}) 

def SignupPage(request):
    if request.method == 'POST':
        if request.POST.get('upname') is not None:
            username = request.POST.get('upname')
            email = request.POST.get('upemail')
            password1 = request.POST.get('uppass1')
            password2 = request.POST.get('uppass2')
            print(username)
            print(email)
            print(password1)
            print(password2)
            if password1 == password2:
                user = User.objects.create_user(username=username, email=email, password=password1)
                us = authenticate(request, username = username, password = password1)
                if us is not None:
                    login(request, us)
                    profile = Profile.objects.create(user_id = request.user.id)
                return redirect('home')
        else:
            print("in")
            username = request.POST.get('username')
            password = request.POST.get('password')
            print(username)
            print(password)

            user = authenticate(request, username = username, password = password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, "signup.html")

    return render(request, 'signup.html')


def LogoutPage(request):
    logout(request)
    return redirect('login')

register = template.Library()
@register.simple_tag(takes_context=True)
@login_required
def profile(request, count = 5):
    if(Profile.objects.filter(user_id = request.user.id) is not None):
        profile = Profile.objects.get(user_id = request.user.id) 
    return render(request, 'profile.html', {'profile' : profile})



def reserve(request, id):
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            table = form.cleaned_data['table']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            # table = Table.objects.get(id=table_id)
            reservation = Reservation(table=table, customer=request.user, start_time=start_time, end_time=end_time)
            if not reservation.is_conflicting():
                reservation.save()
                context = {
                    'table' : table,
                    'start_time' : start_time,
                    'end_time' : end_time
                }
                return render(request, 'success_reserve.html', {'cont' : context})
            else:
                available_table = get_available_tables(start_time, end_time)
                my_data = {'start_time': start_time,
                           'end_time' : end_time,
                           'available_table' : available_table}
                form = Reservation_errorForm(initial = my_data, available_table = available_table)

                cont = {
                    'tables' : available_table,
                    'form' : form,
                }
                return render(request, 'reserve_error.html', cont)
    else:
        form = ReservationForm()
    return render(request, 'reserve.html', {'form' : form})

def success(request):
    return render(request, 'success_reserve.html')

def error(request):
    return render(request, 'reserve_error.html')

from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token

def get_available_tables(start_time, end_time):
    reserved_tables = Reservation.objects.filter(
    Q(start_time__lte = end_time) & Q(end_time__gte = start_time)
    ).values_list('table_id', flat=True)
    available_tables = Table.objects.exclude(id__in = reserved_tables)
    return available_tables 

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

def succes(request, uid):
    email = EmailMessage(
        'subject',
        'body',
        settings.EMAIL_HOST_USER,
        ['210103179@stu.sdu.edu.kz'],
    )

    email.fail_silently = False
    email.send()

    return redirect('home')

from django.contrib.auth import get_user_model

# def activate(request, uidb64, token):
#     User = get_user_model()
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except:
#         user = None

#     if user is not None and account_activation_token.check_token(user, token):
#         user.is_active = True
#         user.save()

#         # messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
#         return redirect('login')
#     # else:
#         # messages.error(request, "Activation link is invalid!")

#     return redirect('home')


# def activateEmail(request, user, to_email):
#     mail_subject = "Activate your user account."
#     message = render_to_string("template_activate_account.html", {
#         'user': user.username,
#         'domain': get_current_site(request).domain,
#         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#         'token': account_activation_token.make_token(user),
#         "protocol": 'https' if request.is_secure() else 'http'
#     })
#     email = EmailMessage(mail_subject, message, to=[to_email])
#     # if email.send():
#         # messages.success(request, f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
#                 # received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
#     # else:
#         # messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')


# def SignupPage(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             # username = form.cleaned_data['username']
#             # email = form.cleaned_data['email']
#             # password = form.cleaned_data['password1']
#             # user = User.objects.create_user(username=username, email=email, password=password)
#             # user = authenticate(username=username, password=password)
#             user = form.save(commit=False)
#             user.is_active = False
#             user.save()
#             activateEmail(request, user, form.cleaned_data.get('email'))
#             return redirect('home')
#             # login(request, user)
#             # return redirect('login')
#         else:
#             for error in list(form.errors.values()):
#                 messages.error(request, error)
#     else:
#         form = RegistrationForm()
#     return render(
#         request=request,
#         template_name="register.html",
#         context={"form": form}
#         )


# Create your views here.
