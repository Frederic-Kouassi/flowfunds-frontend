from django.shortcuts import render

# Create your views here.
def index(request):
    return render (request, 'index.html')


def transaction(request):
    return render (request, 'transaction.html')


def profile (request):
    return render (request, 'profile.html')


def account (request):
    
    return render (request, 'auccount.html')


def add (request):
    
    return render (request, 'add.html')