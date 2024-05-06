from book_review_app.models import Book,APIFeedback
from rest_framework.serializers import ModelSerializer

class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        exclude = ['created_datetime','modified_datetime',]
    
    def to_representation(self, instance):
        user = super(BookSerializer, self).to_representation(instance)
        user['user'] = instance.user.username
        return user

class APIFeedbackserializer(ModelSerializer):
    class Meta:
        model = APIFeedback
        exclude = ['id','date',]
        
    
        
    