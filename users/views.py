from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# attempts to authenticate and login the user
def login_view(request):
    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect("/home")
        else:
            return render(request, 'login.html', {"error": "Incorrect username or password"})
    return render(request, 'login.html', {})

# attempts to create the user object, with error checking
def signup_view(request):
    if request.method == "POST":
        try:
            if User.objects.filter(email=request.POST['email']).exists():
                return render(request, 'signup.html', {"error": "Email already taken"})
            if User.objects.filter(username=request.POST['username']).exists():
                return render(request, 'signup.html', {"error": "Username already taken"})
            user = User.objects.create_user(username=request.POST['username'], email=request.POST['email'], password=request.POST['password'])
            login(request, user)
            return redirect("spotifyconnect")
        except:
            return render(request, 'signup.html', {"error": "Please correctly fill out all required fields"})
    return render(request, 'signup.html', {})

# returns splash page
def splash(request):
    return render(request, 'splash.html', {})

# logs out user
def logout_view(request):
    logout(request)
    return redirect("/")

# displays the about page
def about_view(request):
    return render(request, 'about.html', {})