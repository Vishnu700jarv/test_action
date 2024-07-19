from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView, View
from rest_framework.response import Response
from django.contrib.auth import login
from .models import  CustomUser, Profile, UserActivity, Reward
from .serializers import CreateUserEmailSerializer, CreateUserSerializer,AdminUserSerializer, CreateUserWithNPSerializer, LoginUserSerializer, ProfileSerializer, UserActivitySerializer, RewardSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .utils import OTPManager
from django.http import QueryDict

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

class CreateUserEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(csrf_exempt)
    def post(self, request):
        serializer = CreateUserEmailSerializer(data=request.data)
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
        # First check if the mobile number exists in the system
        mobile = request.data.get('mobile')
        if not CustomUser.objects.filter(mobile=mobile).exists():
            return Response({
                'status': 'error',
                'message': 'No account found with this mobile number'
            }, status=status.HTTP_404_NOT_FOUND)

        # Now handle the login process
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
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(csrf_exempt)
    def post(self, request):
        password = request.data.get('password')
        mobile = request.data.get('mobile')
        otp = request.data.get('otp')
        action = request.data.get('action')  # Can be 'send', 'verify', or 'resend'

        if action in ['send', 'resend']:
            # Check if the user with the provided mobile number exists
            try:
                user_exists = CustomUser.objects.filter(mobile=mobile).exists()
                if not user_exists:
                    return Response({'status': 'error', 'message': 'No account found with this mobile number'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        

class OTPEmailLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(csrf_exempt)
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        otp = request.data.get('otp')
        action = request.data.get('action', '').lower()
        print("*"*100)
        print(request.data)
        print("*"*100)

        # Handling user retrieval with error checking
        user = CustomUser.objects.filter(email=email).first()
        if user:
            mobile = user.mobile
        else:
            return Response({'status': 'error', 'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

        # mobile = '91'+ mobile
        # Handling actions related to OTP
        if action in ['send', 'resend', 'verify']:
            if not mobile or not self.user_exists(mobile):
                return Response({'status': 'error', 'message': 'No account found with this mobile number'}, status=status.HTTP_404_NOT_FOUND)

        # Map action strings to methods
        action_methods = {
            'send': self.send_otp,
            'resend': self.resend_otp,
            'verify': self.verify_otp
        }

        # Execute the appropriate method based on the action
        method = action_methods.get(action)
        if method:
            return method(request, mobile, otp, password)
        else:
            return Response({'status': 'error', 'message': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

    def user_exists(self, mobile):
        # Check if a user exists with a given mobile number
        return CustomUser.objects.filter(mobile=mobile).exists()

    def send_otp(self, request, mobile, otp=None, password=None):
        # Send an OTP to the specified mobile number
        response = OTPManager.send_otp(mobile)
        return Response({'status': 'success', 'message': 'OTP sent successfully', 'data': response}, status=status.HTTP_200_OK)

    def verify_otp(self, request, mobile, otp, password):
        # Verify the OTP sent to the specified mobile number
        if not otp:
            return Response({'status': 'error', 'message': 'OTP is required'}, status=status.HTTP_400_BAD_REQUEST)

        is_valid, message = OTPManager.verify_otp(mobile, otp)
        if is_valid:
            # Since request.data is immutable, we need to copy it to be able to modify
            mutable_data = request.data.copy() if isinstance(request.data, QueryDict) else dict(request.data)
            mutable_data['mobile'] = mobile  # Append mobile number to the data

            serializer = LoginUserSerializer(data=mutable_data, context={'request': request})
            if serializer.is_valid():
                user = serializer.validated_data['user']
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
            else:
                return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'status': 'error', 'message': message}, status=status.HTTP_400_BAD_REQUEST)
        
    def resend_otp(self, request, mobile, otp=None, password=None):
        # Resend the OTP to the specified mobile number
        response = OTPManager.resend_otp(mobile)
        return Response({'status': 'success', 'message': 'OTP resent successfully', 'data': response}, status=status.HTTP_200_OK)



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

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated]  #