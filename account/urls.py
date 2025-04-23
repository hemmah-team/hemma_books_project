from django.urls import path

from .views import changeNumberView, loginView, registerView

urlpatterns = [
    path("register/", registerView),
    path("login/", loginView),
    path("change_number/", changeNumberView),
]
