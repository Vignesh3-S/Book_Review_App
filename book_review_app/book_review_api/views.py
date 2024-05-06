from .serializers import BookSerializer,APIFeedbackserializer
from book_review_app.models import User,ApiUser,Book,APIFeedback
from rest_framework.views import APIView
from django.utils.http import  urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.pagination import PageNumberPagination

class BookApiList(APIView,PageNumberPagination):
    def get(self,request,email,token):
        get_token = token
        try:
            dec_email=urlsafe_base64_decode(force_str(email)).decode()
            user = User.objects.get(email=dec_email)
            user=ApiUser.objects.get(user=user.id)    
        except:
            return Response({"error":'User Not Found'},status=status.HTTP_404_NOT_FOUND)
        if user.token == get_token:
            data = Book.objects.all()
            pag_data=self.paginate_queryset(data,request)
            if pag_data is not None:
                serializer = BookSerializer(pag_data,many=True)
                return self.get_paginated_response(serializer.data)
        else:
            return Response({'error':'Invalid Token'},status=status.HTTP_400_BAD_REQUEST)
        
    def post(self,request,email,token):
        get_token = token
        try:
            dec_email=urlsafe_base64_decode(force_str(email)).decode()
            user = User.objects.get(email=dec_email)
            user=ApiUser.objects.get(user=user.id)    
        except:
            return Response({"error":'User Not Found'},status=status.HTTP_404_NOT_FOUND)
        
        if user.token == get_token:
            try:
                query = request.data['search']
                if Book.objects.filter(bookname__icontains = query):
                    name = Book.objects.filter(bookname__icontains = query)
                elif Book.objects.filter(bookauthor__icontains = query):
                    name = Book.objects.filter(bookauthor__icontains = query)
                elif Book.objects.filter(booktype__icontains = query):
                    name = Book.objects.filter(booktype__icontains = query)
                else:
                    return Response({'error':'Invalid search pattern. Try Again With Different Names.'},status=status.HTTP_404_NOT_FOUND)
            except:
                return Response({'error':'No Search Value.'},status=status.HTTP_400_BAD_REQUEST)
            
            serializer = BookSerializer(name,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response({'error':'Invalid Token'},status=status.HTTP_400_BAD_REQUEST)

class BookApiOne(APIView):
    throttle_classes=[ScopedRateThrottle]
    throttle_scope = 'book_one'
    def get(self,request,email,token,id):
        get_token = token
        try:
            dec_email=urlsafe_base64_decode(force_str(email)).decode()
            user = User.objects.get(email=dec_email)
            user=ApiUser.objects.get(user=user.id)    
        except:
            return Response({'error':'User Not Found'},status=status.HTTP_404_NOT_FOUND)
        if user.token == get_token:
            data = Book.objects.get(id=id)
            serializer = BookSerializer(data)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response({'error':'Invalid Token'},status=status.HTTP_400_BAD_REQUEST) 
    
    
    def post(self,request,email,token,id):
        get_token = token
        try:
            dec_email=urlsafe_base64_decode(force_str(email)).decode()
            user = User.objects.get(email=dec_email)
            user=ApiUser.objects.get(user=user.id)    
        except:
            return Response({'error':'User Not Found'},status=status.HTTP_404_NOT_FOUND)
        if user.token == get_token:
            try:
                name = request.data['username']
                feedbk = request.data['feedback']
                app = user.app_name
                bookname = id
                try:
                    check_instance = APIFeedback.objects.filter(username = name, application = app, book = bookname)
                    if check_instance:
                        return Response({'error':'User with this username already gave feedback'},status=status.HTTP_404_NOT_FOUND)
                except:
                    pass
                serializer = APIFeedbackserializer(data={'application':app,'username':name,'book':bookname,'feedback':feedbk})
                if serializer.is_valid():
                    serializer.save()
                    return Response({'success':'Thanks for you feedback.'},status=status.HTTP_201_CREATED)
                else:
                    return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({'error':'invalid values'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error':'Invalid Token'},status=status.HTTP_400_BAD_REQUEST)
          
