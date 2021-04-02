from django.urls import path

from .api import UserList


app_name = "registration"

urlpatterns = [
    path("", UserList.as_view(), name="listcreate"),
]
