import http.client
import json
import random
from django.conf import settings
from django.utils import timezone
from .models import OTP

class OTPManager:
    @staticmethod
    def generate_otp():
        return ''.join([str(random.randint(0, 9)) for _ in range(4)])

    @staticmethod
    def send_otp(mobile_number):
        otp = OTPManager.generate_otp()
        payload_dict = {
            "template_id": settings.MSG91_TEMPLATE_ID,
            "short_url": "1",
            "recipients": [
                {
                    "mobiles": mobile_number,
                    # "service_name": "Your Service Name",
                    "OTP": otp
                }
            ]
        }
        payload = json.dumps(payload_dict)
        headers = {
            'authkey': settings.MSG91_AUTH_KEY,
            'Accept': "application/json",
            'Content-Type': "application/json"
        }
        
        # conn = http.client.HTTPSConnection(settings.OTP_SENDER_DN)
        conn = http.client.HTTPSConnection("control.msg91.com")
        try:
            conn.request("POST", "/api/v5/flow", payload, headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
            OTP.objects.update_or_create(
                mobile_number=mobile_number,
                defaults={'otp': otp, 'created_at': timezone.now()}
            )
            return data
        except Exception as e:
            raise Exception(f"An error occurred: {str(e)}")
        finally:
            conn.close()

    @staticmethod
    def verify_otp(mobile_number, user_otp):
        try:
            otp_instance = OTP.objects.get(mobile_number=mobile_number, otp=user_otp)
            if otp_instance.is_expired():
                otp_instance.delete()
                return False, "OTP expired"
            otp_instance.delete()
            return True, "OTP verified successfully"
        except OTP.DoesNotExist:
            return False, "Invalid OTP"

    @staticmethod
    def resend_otp(mobile_number):
        OTP.objects.filter(mobile_number=mobile_number).delete()
        return OTPManager.send_otp(mobile_number)
