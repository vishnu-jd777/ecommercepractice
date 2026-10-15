from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, ProfileForm


def register_view(request):

    # 1. If already logged in, go to the store home page
    if request.user.is_authenticated:
        return redirect("store:home")

    # 2. Create the form, with submitted data if any
    form = SignUpForm(request.POST or None)

    # 3. Process the submitted form
    if request.method == "POST" and form.is_valid():

        user = form.save()
        login(request, user) #this login() method establishes the authenticated session

        messages.success(request, "Welcome! Your account was created.")

        return redirect("store:home")

    # 4. Display the form
    return render(request, "accounts/signup.html", {"form": form})

@login_required
def profile_view(request):
    return render(request,'accounts/profile.html')

@login_required
def edit_profile_view(request):
    form = ProfileForm(request.POST or None,instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request,'Profile Updated')
        return redirect("accounts:profile")
    return render(request,'accounts/edit_profile.html', {'form' : form})

