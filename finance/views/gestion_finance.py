from django.shortcuts import render,  redirect
from django.views import View
from django.contrib import messages





class IndexView(View):
    template=  'global_data/index.html'
    def get(self, request):
        return render(request,self.template)


class TransactionView(View):
    template= 'global_data/transaction.html'
    def get(self, request):
        return render(request, self.template )



class AccountView(View):
    template= 'global_data/account.html'
    def get(self, request):
        return render(request,self.template )


class AddView(View):
    template= 'global_data/add.html'
    def get(self, request):
        return render(request, self.template)
