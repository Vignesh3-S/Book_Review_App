from django import forms
from django.forms import TextInput,EmailInput,Textarea
from .models import Contact,User,Book,Feedback,ApiUser
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

# user register form
class Usercreateform(forms.ModelForm):
    password = forms.CharField(label='',max_length=15,min_length=8,widget=forms.PasswordInput(attrs={'placeholder':_('Password'), 'class':"form-control",
            "data-toggle" : "password"}),help_text=_("Create a strong password with alphanumeric and special characters."),
            validators=[validate_password])
    confirm_password = forms.CharField(label='',max_length=15,min_length=8,widget=forms.PasswordInput(attrs={'placeholder':_('Confirm Password'), 'class':"form-control",
            "data-toggle" : "password"}),help_text=_("Re-enter the password."))
    
    class Meta():
        model = User
        fields = ("username","email","mobilenumber",)
        labels = {
            "username": (""),
            "email": (""),
            "mobilenumber":(""),
        }
        widgets = {
            "username": TextInput(attrs={'placeholder':_('Full Name')}),
            "email": EmailInput(attrs={'placeholder':_('Email')}),
            "mobilenumber": PhoneNumberPrefixWidget(attrs={'placeholder':_('Mobile'), 'class': "form-control"}),
        }

# user login form
class Userloginform(forms.Form):
    email = forms.EmailField(label="",widget=forms.EmailInput(attrs={'placeholder':_('Email'),'class':'form-control','required':True}))
    captcha = ReCaptchaField(label = '',widget=ReCaptchaV2Checkbox)
    password = forms.CharField(label='',max_length=15,min_length=8,widget=forms.PasswordInput(attrs={'placeholder':_('Password'), 'class':"form-control",
                "data-toggle" : "password"}))

# user contact form
class Contactform(forms.ModelForm):
    class Meta():
        model = Contact
        fields = '__all__'

# user Book Form
class UserBookForm(forms.ModelForm):
    bookimg = forms.ImageField(label = "Book Image",required=False)
    bookfile = forms.FileField(label = "Book File",required=False)
    class Meta():
        model = Book
        exclude = ('user','created_datetime','modified_datetime','bookimg','bookfile',)
        labels = {
            "bookname":(""),"bookauthor":(""),"booktype":("Genere"),
        }
        widgets = {
            "bookname":TextInput(attrs={'placeholder':_('Book Titile')}),
            "bookauthor":TextInput(attrs={'placeholder':_('Book Author')}),
        }

# user image form
class Userimageform(forms.Form):
    image = forms.ImageField(label = "User Image",required=False,help_text="file extension must be .jpg, .jpeg, .png")

# user update form
class Userupdateform(forms.ModelForm):
    class Meta():
        model = User
        fields = ('username','mobilenumber',)
        labels = {'username':(""),'mobilenumber':(""),}
        widgets = {
            'username' : TextInput(attrs={'placeholder':_("Username"),'class':'form-control'}),
            "mobilenumber": PhoneNumberPrefixWidget(attrs={'placeholder':_('Mobile'), 'class': "form-control"}),
        }

# Feedback form
class Feedbackform(forms.ModelForm):
    class Meta():
        model = Feedback
        fields = ('feedback',)
        labels = {'feedback':(""),}
        widgets = {
            'feedback' : Textarea(attrs={'placeholder':_("Feedback about the review"),'class' :'form-control'}),
        }

# Password change - email form
class Emailform(forms.Form):
    email = forms.EmailField(label='',widget=forms.EmailInput(attrs={'placeholder':'Enter the email to receive link','class':'form-control'}))       

# password reset form
class PasswordChangeForm(forms.Form):
    password = forms.CharField(label='', help_text="Password must be atleast 8 characters, should contain alphnumeric and special characters.",
                                max_length=15,min_length=8,validators=[validate_password],widget=forms.PasswordInput(attrs={'placeholder':'Password', 'class':"form-control"}))
    confirm_password = forms.CharField(label='',help_text="Password and confirm password must be same.",
                                max_length=15,min_length=8,widget=forms.PasswordInput(attrs={'placeholder':'Confirm Password', 'class':"form-control"}))

# forgot api form
class ForgotApiForm(forms.ModelForm):
    password = forms.CharField(label='',max_length=15,min_length=8,widget=forms.PasswordInput(attrs={'placeholder':'Password', 'class':"form-control"}))
    class Meta():
        model = ApiUser
        fields = ('app_type','app_name',)
        labels = {'app_type':(""),'app_name':(""),}
        widgets = {
            'app_type' : TextInput(attrs={'placeholder':_("Application Type"),'class' :'form-control'}),
            'app_name' : TextInput(attrs={'placeholder':_("Application Name"),'class' :'form-control'}),
        }

        