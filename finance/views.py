from django.shortcuts import render

# Create your views here.
def index(request):
    return render (request, 'global_data/index.html')


def transaction(request):
    return render (request, 'global_data/transaction.html')


def profile (request):
    return render (request, 'global_data/profile.html')


def account (request):
    
    return render (request, 'global_data/account.html')


def add (request):
    
    return render (request, 'global_data/add.html')