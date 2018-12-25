import json
import random
from unittest.mock import Mock

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import get_user_model

from .utils import Utils
from .models import UserToken

User = get_user_model()

# mocking black box apis
utils = Utils()
utils.sent_token = Mock(return_value="123232")
utils.verify_token = Mock(return_value=True)

# creating a random token and saving it in db
def create_token(user):
    key = random.getrandbits(128)
    expire_date = timezone.now() + timezone.timedelta(days=30)
    token_obj = UserToken(user=user, key=key, expire_date=expire_date)
    token_obj.save()
    return token_obj

# a helper method for getting token from header and authentication
def authenticate_with_token(request):
    auth = request.META.get('HTTP_AUTHORIZATION')
    if not auth:
        return False
    auth = auth.split()
    if not auth or auth[0].lower() != 'bearer' or len(auth) != 2:
        return False

    token = auth[1]
    user_token = UserToken.objects.filter(
        key=token,
        expire_date__gt=timezone.now()
    )
    if user_token.first():
        return True
    return False

@csrf_exempt
def login_with_phone_number(request):
    if request.method == "POST":
        phone_number = request.POST.get('phone_number')
        if not phone_number or len(phone_number) != 11:
            return HttpResponse(
                json.dumps({'Error': "Please enter your phone number"}),
                status="400"
            )
        try:
            utils.sent_token(phone_number)
            try:
                User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                User(phone_number=phone_number).save()
            return HttpResponse(
                json.dumps({'Success': "Confirmation code sends shortly."}),
                status="200"
            )
        except Exception as e:
            return HttpResponse(
                json.dumps({'Error': str(e)}),
                status="400"
            )
    return HttpResponse(
        json.dumps({'Error': "Invalid request"}),
        status="400"
    )

@csrf_exempt
def login_with_phone_number_confirmation(request):
    if request.method == "POST":
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        if not phone_number or not password:
            return HttpResponse(
                json.dumps({'Error': "Please enter your phone number and password"}),
                status="400"
            )
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return HttpResponse(
                json.dumps({'Error': "Please enter valid phone number"}),
                status="400"
            )
        if not utils.verify_token(phone_number, password):
            return HttpResponse(
                json.dumps({'Error': "Invalid phone_number/password"}),
                status="400"
            )
        token = create_token(user)
        return HttpResponse(
            json.dumps({'token': token.key}),
            status=200,
            content_type="application/json"
        )
    return HttpResponse(
        json.dumps({'Error': "Invalid phone_number/password"}),
        status="400"
    )

# purpose of this view is to show whether authenrication works or not
def test_api(request):
    if not authenticate_with_token(request):
        return HttpResponse(
            json.dumps({'Error': "Invalid token"}),
            status="401"
        )
    return HttpResponse(
        json.dumps({'Success': "You can see the content"}),
        status="200"
    )
