from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.db import IntegrityError
from .models import User,Product,Order  # Import your User model

def home(request):
    details = None
    if request.method == "GET":
        details = request.GET.get("details")
        if details:
            # Process the details if needed
            pass
    return render(request, "home.html", {'details': details})

def about(request):
    return render(request, "aboutUs.html")

def location(request):
    return render(request, "location.html")

def register(request):
    register = {}
    try:
        if request.method == "POST":
            firstName = request.POST.get("firstName")
            lastName = request.POST.get("lastName")
            phone = request.POST.get("phone")
            email = request.POST.get("email")
            dob = request.POST.get("dob")
            address = request.POST.get("address")
            password = make_password(request.POST.get("password"))
            role = request.POST.get("role", "user")
            joinedDate = timezone.now()

            # Check if email already exists using ORM
            if User.objects.filter(email=email).exists():
                register['error'] = "Email is already registered."
                # Keep the previous data to display in the form
                register['firstName'] = firstName
                register['lastName'] = lastName
                register['phone'] = phone
                register['email'] = email
                register['dob'] = dob
                register['address'] = address
            else:
                # Create new user using ORM
                User.objects.create(
                    firstName=firstName,
                    lastName=lastName,
                    phone=phone,
                    email=email,
                    dob=dob,
                    address=address,
                    password=password,
                    role=role,
                    joinedDate=joinedDate
                )
                return HttpResponseRedirect("/login/")

    except IntegrityError as e:
        register['error'] = "Email is already registered."
        # Keep the previous data to display in the form
        register['firstName'] = request.POST.get("firstName", "")
        register['lastName'] = request.POST.get("lastName", "")
        register['phone'] = request.POST.get("phone", "")
        register['email'] = request.POST.get("email", "")
        register['dob'] = request.POST.get("dob", "")
        register['address'] = request.POST.get("address", "")
    except Exception as e:
        register['error'] = str(e)

    return render(request, "register.html", register)

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            # Query the database using ORM
            user = User.objects.get(email=email)
            
            # Verify password
            if check_password(password, user.password):
                # Login successful - store user data in session
                request.session['user_id'] = user.id
                request.session['user_email'] = user.email
                request.session['user_role'] = user.role
                request.session.set_expiry(3600)  # Session expires in 1 hour
                
                # Check user role and redirect accordingly
                if user.role == 'Admin':
                    return HttpResponseRedirect("/adminPanel/")
                else:
                    return HttpResponseRedirect("/home/")
            else:
                # Invalid password
                error = "Invalid email or password"
                return render(request, "login.html", {'error': error})
                
        except User.DoesNotExist:
            # User with this email doesn't exist
            error = "Invalid email or password"
            return render(request, "login.html", {'error': error})

    # GET request - show login form
    return render(request, "login.html")
def logout_view(request):
    # Clear the session
    request.session.flush()

    # Optionally, add a message here (if you use messages framework)

    # Redirect to login or home page
    return redirect('home')  # or redirect('home')
