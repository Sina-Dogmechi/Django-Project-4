from rest_framework.views import APIView
from .serializers import UserSerializer, UserRegisterSerializer, ChangePasswordSerializer
from rest_framework.response import Response
from rest_framework import status
from .services import create_user, update_profile, change_password, deactivate_user
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .selectors import get_user_by_id


class UserRegisterView(APIView):

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user(email=serializer.validated_data['email'], username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        username = request.data.get('username')
        user = update_profile(user=request.user, username=username)
        return Response(UserSerializer(user).data)



class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        change_password(user=request.user, new_password=serializer.validated_data['new_password'])
        return Response({'message': 'password changed successfully'})


class UserDeactivateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        user = get_user_by_id(pk)
        if not user:
            return Response({'message': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        deactivate_user(user=user)
        return Response({'message': 'user deactivated'}, status=status.HTTP_200_OK)
