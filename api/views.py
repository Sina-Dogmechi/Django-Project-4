from rest_framework.views import APIView
from .serializers import UserSerializer, UserRegisterSerializer
from rest_framework.response import Response
from rest_framework import status
from .services import create_user


class UserRegisterView(APIView):

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user(email=serializer.validated_data['email'], username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
