
from django.contrib import admin
from django.urls import path

from finance.views.auth_views import *
from finance.views.gestion_finance import *
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name="index"),
    path('transaction/', TransactionView.as_view(), name="transaction"),
    path('profile/', ProfileView.as_view(), name="profile"),
    path('account/', AccountView.as_view(), name="account"),
    path('add/', AddView.as_view(), name="add"),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout')

]

