from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from .managers import Book_users_manager
from django.utils.translation import gettext_lazy as _
from cloudinary_storage.storage import VideoMediaCloudinaryStorage

class User(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(verbose_name= "FullName" ,max_length= 35)
    email = models.EmailField(verbose_name='Email', unique = True)
    mobilenumber = PhoneNumberField(verbose_name="Mobile")
    userimg = models.ImageField(verbose_name='UserImages', upload_to="userimages",null = True,blank=True)
    date_joined = models.DateTimeField(auto_now_add=True,verbose_name='Account_Created')
    date_modified = models.DateTimeField(auto_now=True,verbose_name='Account_Modified')
    last_login = models.DateTimeField(auto_now=True,verbose_name='last_login')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_BRS_account = models.BooleanField(default = False)
    count = models.IntegerField(verbose_name="API Count",default=0)
    
    objects = Book_users_manager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','password',]
    
    def __str__(self):
        return self.username

class Book(models.Model):
    user = models.ForeignKey("User",on_delete=models.CASCADE,verbose_name="User_id")
    bookname = models.CharField(verbose_name="Book Name",max_length=50)
    bookauthor = models.CharField(verbose_name='Book Author',max_length=50)
    booktypechoices= [('fantasy','fantasy'),('romance novel','romance novel'),('autobiography','autobiography'),('biography','biography'),
                      ('mystery','mystery'),('memoir','memoir'),('horror','horror'),('philosophy','philosophy'),
                      ('cookbook','cookbook'),("children's literature","children's literature"),('anthology','anthology'),('nonfiction','nonfiction'),
                      ('short story','short story'),('drime','drime'),('dncyclopedia','dncyclopedia'),('dairy','dairy'),
                      ('politics','politics'),('biblophile','biblophile'),('fable','fable'),('fiction','fiction'),]
    booktype = models.CharField(verbose_name= "BookType" , max_length = 30 , choices=booktypechoices)
    bookimg = models.ImageField(verbose_name='BookImages', upload_to="bookimages",
                                help_text=_("file extension must be .jpg, .jpeg, .png"),blank=True)
    bookfile =models.FileField(verbose_name="Bookaudios", upload_to="bookaudios",storage=VideoMediaCloudinaryStorage()
                               ,blank=True)
    created_datetime = models.DateTimeField(auto_now_add=True,verbose_name='Book_Created')
    modified_datetime =  models.DateTimeField(auto_now=True,verbose_name='Book_Modified')

    def __str__(self):
         return self.bookname
    
class Feedback(models.Model):
    user = models.ForeignKey("User",on_delete=models.CASCADE,verbose_name = "User")
    book = models.ForeignKey("Book",on_delete=models.CASCADE,verbose_name="Book")
    feedback = models.TextField(verbose_name="Feedback",null=True)
    date = models.DateTimeField(auto_now_add=True,verbose_name="Feedback Created")

    def __str__(self):
        return f'{self.user}-{self.book} feedback'

class APIFeedback(models.Model):
    application=models.CharField(max_length=50,verbose_name="App Name")
    username = models.CharField(max_length=50,verbose_name="Username")
    book = models.ForeignKey("Book",on_delete=models.CASCADE,verbose_name="Book")
    feedback = models.TextField(verbose_name="Feedback",null=True)
    date = models.DateTimeField(auto_now_add=True,verbose_name="Feedback Created")
    
    def __str__(self):
        return f'{self.application}--{self.username}--{self.book} feedback'
    
class Contact(models.Model):
    Name = models.CharField(max_length=30,verbose_name="Name")
    email = models.EmailField(verbose_name="Email")
    message = models.TextField(verbose_name="Message")


    def __str__(self):
        return f"{self.Name}'s Message"
    
class ApiUser(models.Model):
    user = models.OneToOneField("User",on_delete=models.CASCADE,verbose_name="API User")
    app_name =  models.CharField(max_length=200,verbose_name="App Name")
    app_type =  models.CharField(max_length=200,verbose_name="App Type")
    token = models.CharField(verbose_name="Token",max_length=40)
    is_valid = models.BooleanField(verbose_name="Token Valid")
    date = models.DateTimeField(auto_now_add=True,verbose_name="Date and Time")
    
    def __str__(self):
        return f"{self.user}'s Token"
    
