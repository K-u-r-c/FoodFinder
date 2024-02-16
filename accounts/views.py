from django.shortcuts import redirect, render
from .models import User
from .forms import UserForm
from django.contrib import messages

def registerUser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, 'User registered successfully')
            return redirect('registerUser')
        else:
            messages.error(request, 'User registration failed')
    else:
        form = UserForm()
        
    context = {
        'form': form
    }
    return render(request, 'accounts/registerUser.html', context)