from django.shortcuts import render
from .serializers import RegisterSerializer, UpdatePasswordSerializer
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from .models import CustomUser
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate    
from rest_framework.response import Response
from rest_framework import status
class RegisterView(CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class UpdatePasswordView(APIView):
    def post(self,request,*args,**kwargs):
        current_user = authenticate(email=request.user.email,password=request.data["old_password"])
        print(current_user.first_name)
        if(current_user is not None):
            serializer = UpdatePasswordSerializer(data=request.data)
            if serializer.is_valid():
                current_user.set_password(request.data['new_password'])
                current_user.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(data="Password must have minimum 6 length and should have alphabets and number",status=status.HTTP_406_NOT_ACCEPTABLE)

        return Response(data="User not authenticated",status=status.HTTP_401_UNAUTHORIZED)

class VerifyTokenView(APIView):
    permission_classes = (AllowAny,)
    def get(self,request,*args,**kwargs):
        if self.request.user.is_anonymous:
            print("not logged")
            return Response(data={"logged":False},status=status.HTTP_200_OK)
        return Response(data={"logged":True},status=status.HTTP_200_OK)