import datetime
import json
import random
from unittest.mock import Mock
import jwt

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.conf import settings

from .utils import Utils

User = get_user_model()

# mocking black box apis
utils = Utils()
utils.sent_token = Mock(return_value="123232")
utils.verify_token = Mock(return_value=True)


def create_token(user):
    """Create jwt token based on users phone number"""
    payload = {
        'phone_number': user.phone_number,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
    }
    return jwt.encode(payload, settings.SECRET_KEY)



def authenticate_with_token(request):
    """Helper method for getting token from header and authenticate"""
    auth = request.META.get('HTTP_AUTHORIZATION')
    if not auth:
        return False
    auth = auth.split()
    if not auth or auth[0].lower() != 'bearer' or len(auth) != 2:
        return False

    token = auth[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
    except jwt.ExpiredSignatureError:
        return False
    
    try:
        User.objects.get(phone_number=payload['phone_number'], active=True)
    except User.DoesNotExist:
        return False
    return True

@csrf_exempt
def login_with_phone_number(request):
    phone_number = request.POST.get('phone_number')
    if not phone_number or len(phone_number) != 11:
        return JsonResponse(
            {'Error': "Please enter your phone number"},
            status="400"
        )
    try:
        utils.sent_token(phone_number)
        try:
            User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            User(phone_number=phone_number).save()
        return JsonResponse(
            {'Success': "Confirmation code sends shortly."},
            status="200"
        )
    except Exception as e:
        return JsonResponse(
            {'Error': str(e)},
            status="400"
        )

@csrf_exempt
def login_with_phone_number_confirmation(request):
    phone_number = request.POST.get('phone_number')
    password = request.POST.get('password')
    if not phone_number or not password:
        return JsonResponse(
            {'Error': "Please enter your phone number and password"},
            status="400"
        )
    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        return JsonResponse(
            {'Error': "Please enter valid phone number"},
            status="400"
        )
    if not utils.verify_token(phone_number, password):
        return JsonResponse(
            {'Error': "Invalid phone_number/password"},
            status="400"
        )
    token = create_token(user)
    return JsonResponse(
        {'token': token.decode('utf-8')},
        status=200,
    )

def test_api(request):
    if not authenticate_with_token(request):
        return JsonResponse(
            {'Error': "Invalid token"},
            status="401"
        )
    return JsonResponse(
        {'Success': "You can see the content"},
        status="200"
    )
