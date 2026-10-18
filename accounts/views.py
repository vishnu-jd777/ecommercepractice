from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, ProfileForm, AddressForm
from . models import Address


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
    return render(request, "accounts_templates/signup.html", {"form": form})

@login_required
def profile_view(request):
    return render(request,'accounts_templates/profile.html')

@login_required
def edit_profile_view(request):
    form = ProfileForm(request.POST or None,instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request,'Profile Updated')
        return redirect("accounts:profile")
    return render(request,'accounts_templates/edit_profile.html', {'form' : form})

@login_required
def address_list_view(request):
    addresses = request.user.addresses.all()
    return render(request,'accounts_templates/address_list.html',{'addresses': addresses})

@login_required
def add_address_view(request):
    form = AddressForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()

        messages.success(request, 'Address added')

        next_url = request.GET.get('next')

        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()}
        ):
            return redirect(next_url)

        return redirect('accounts:address_list')

    return render(
        request,
        'accounts_templates/address_form.html',
        {'form': form, 'title': 'Add Address'}
    )

@login_required
def edit_address_view(request,pk):
    address = get_object_or_404(Address,pk=pk,user=request.user)
    form = AddressForm(request.POST or None, instance=address)
    if form.is_valid():
        form.save()
        messages.success(request,'Address Updated Successfully')
        return redirect('accounts:address_list')
    return render(request,'accounts_templates/address_form.html',{'form' : form,'title': 'Edit address'})

@login_required
def delete_address_view(request,pk):
    address = get_object_or_404(Address,pk=pk,user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request,'Address Deleted Successfully')
        return redirect('accounts:address_list')
    return redirect('accounts:address_list')


