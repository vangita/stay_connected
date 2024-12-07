from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import SignUpSerializer, SignInSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
# from django_rest_passwordreset.signals import reset_password_token_created

class SignUpAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignInAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')

            if not refresh_token:
                return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#
# class PasswordResetEmailHandler:
#
#     @staticmethod
#     def send_email(reset_password_token, request):
#         reset_password_url = "{}?token={}".format(
#             request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
#             reset_password_token.key
#         )
#
#         email_plaintext_message = (
#             f"Hello {reset_password_token.user.username},\n\n"
#             f"You requested a password reset for your account.\n\n"
#             f"To reset your password, please use the following link:\n\n"
#             f"{reset_password_url}\n\n"
#         )
#
#         msg = EmailMultiAlternatives(
#             subject="Password Reset for Your Website",
#             body=email_plaintext_message,
#             from_email="noreply@yourwebsite.com",
#             to=[reset_password_token.user.email],
#         )
#         msg.send()
#
#     @classmethod
#     def handle_signal(cls, sender, instance, reset_password_token, *args, **kwargs):
#         cls.send_email(reset_password_token, instance.request)


# reset_password_token_created.connect(PasswordResetEmailHandler.handle_signal)

