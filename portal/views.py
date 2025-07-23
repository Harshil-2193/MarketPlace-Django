from django.shortcuts import render, HttpResponse



# Login And Register
def login_view(request):
    return render(request, 'auth/login.html')
def register_view(request):
    return render(request, 'auth/register.html')

# Dashboard
def portal(request):
    return render(request, 'portal/dashboard.html')