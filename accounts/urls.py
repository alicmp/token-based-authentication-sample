from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$', views.login_with_phone_number, name='login'),
    url(r'^confirmation/$', views.login_with_phone_number_confirmation, name='confirmation'),
    url(r'^test/$', views.test_api, name='test_api'),
]