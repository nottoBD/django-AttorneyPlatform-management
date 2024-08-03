from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/accounts/login")
def home(request):
    return render(request, 'neok/home.html')

def privacy_view(request):
    return render(request, 'cookiebanner/privacy.html')