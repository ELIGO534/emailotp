from django.shortcuts import render
import random
import string
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import json
from django.conf import settings

@csrf_exempt
def send_email_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return JsonResponse({"error": "Email is required"}, status=400)

            otp = ''.join(random.choices(string.digits, k=6))

            # Store OTP in cache for 5 minutes
            cache.set(f"email_otp_{email}", otp, timeout=300)

            send_mail(
                subject="Your OTP Code",
                message=f"Your OTP is {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            return JsonResponse({"message": "OTP sent successfully"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.http import JsonResponse
import json

@csrf_exempt
def verify_email_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            otp = data.get("otp")

            if not email or not otp:
                return JsonResponse({"status": "error", "message": "Email and OTP required"}, status=400)

            cached_otp = cache.get(f"email_otp_{email}")
            if cached_otp is None:
                return JsonResponse({"status": "fail", "message": "OTP expired or not found"}, status=400)

            if otp == cached_otp:
                cache.delete(f"email_otp_{email}")
                return JsonResponse({"status": "success", "message": "OTP verified"})
            else:
                return JsonResponse({"status": "fail", "message": "Invalid OTP"}, status=400)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)


from django.shortcuts import render
import random
import string
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings

def send_otp_form(request):
    message = ""
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            otp = ''.join(random.choices(string.digits, k=6))
            cache.set(f"email_otp_{email}", otp, timeout=300)

            send_mail(
                subject="Your OTP Code",
                message=f"Your OTP is {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            message = f"OTP sent to {email}"

    return render(request, "send_otp_test.html", {"message": message})
