from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView, View
from rest_framework.response import Response
from django.contrib.auth import login
from .models import  CustomUser, Profile, UserActivity, Reward
from .serializers import CreateUserSerializer, CreateUserWithNPSerializer, LoginUserSerializer, ProfileSerializer, UserActivitySerializer, RewardSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .utils import OTPManager

class SendOTPView(APIView):
    def get(self, request):
        mobile_number = request.GET.get('mobile')
        if mobile_number:
            try:
                response = OTPManager.send_otp(mobile_number)
                return JsonResponse({'status': 'success', 'message': 'OTP sent successfully', 'data': response})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            return JsonResponse({'status': 'error', 'message': 'Mobile number is required'})

class VerifyOTPView(View):
    def get(self, request):
        mobile_number = request.GET.get('mobile')
        otp = request.GET.get('otp')
        if mobile_number and otp:
            is_valid, message = OTPManager.verify_otp(mobile_number, otp)
            if is_valid:
                return JsonResponse({'status': 'success', 'message': message})
            else:
                return JsonResponse({'status': 'error', 'message': message})
        else:
            return JsonResponse({'status': 'error', 'message': 'Both mobile number and OTP are required'})

class ResendOTPView(View):
    def get(self, request):
        mobile_number = request.GET.get('mobile')
        if mobile_number:
            try:
                response = OTPManager.resend_otp(mobile_number)
                return JsonResponse({'status': 'success', 'message': 'OTP resent successfully', 'data': response})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            return JsonResponse({'status': 'error', 'message': 'Mobile number is required'})


class CreateUserView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(csrf_exempt)
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully.", "user_id": user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateAccountWithEmptyPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(csrf_exempt)
    def post(self, request):
        serializer = CreateUserWithNPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # save the user with the password handled in the serializer
            return Response({
                "message": "OTP verified and user account activated successfully.",
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginUserView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(csrf_exempt)
    def post(self, request):
        serializer = LoginUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)

            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user_info': {
                    'username': user.first_name + ' ' + user.last_name,
                    'mobile': user.mobile,
                    'email': user.email
                    # Add more fields as needed
                },
                'message': 'User logged in successfully.'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(csrf_exempt)
    def post(self, request):
        mobile = request.data.get('mobile')
        otp = request.data.get('otp')
        action = request.data.get('action')  # Can be 'send', 'verify', or 'resend'

        if action == 'send':
            try:
                response = OTPManager.send_otp(mobile)
                return Response({'status': 'success', 'message': 'OTP sent successfully', 'data': response}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        elif action == 'verify':
            if mobile and otp:
                is_valid, message = OTPManager.verify_otp(mobile, otp)
                if is_valid:
                    try:
                        user = CustomUser.objects.get(mobile=mobile)
                        login(request, user)
                        refresh = RefreshToken.for_user(user)
                        return Response({
                            'access_token': str(refresh.access_token),
                            'refresh_token': str(refresh),
                            'user_info': {
                                'username': user.first_name + ' ' + user.last_name,
                                'mobile': user.mobile,
                                'email': user.email
                            },
                            'message': 'User logged in successfully.'
                        }, status=status.HTTP_200_OK)
                    except CustomUser.DoesNotExist:
                        return Response({'status': 'error', 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'status': 'error', 'message': message}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'status': 'error', 'message': 'Both mobile number and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        elif action == 'resend':
            try:
                response = OTPManager.resend_otp(mobile)
                return Response({'status': 'success', 'message': 'OTP resent successfully', 'data': response}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'status': 'error', 'message': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Assuming each user has one profile and Profile model has user field
        return Profile.objects.filter(user=self.request.user)

class UserActivityViewSet(viewsets.ModelViewSet):
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Assuming UserActivity model has a user field that links to the Django user
        return UserActivity.objects.filter(user=self.request.user)

class RewardViewSet(viewsets.ModelViewSet):
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Assuming Reward model has a user field
        return Reward.objects.filter(user=self.request.user)
