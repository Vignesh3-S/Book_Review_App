from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib import messages
from .forms import (Usercreateform,Contactform,Userloginform,UserBookForm,Userimageform,Userupdateform,
Feedbackform,Emailform,PasswordChangeForm,ForgotApiForm)
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from phonenumber_field.validators import validate_international_phonenumber
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import phonenumbers
from django.contrib.auth.hashers import check_password
from django.template.loader import render_to_string
from .models import User,Book,Feedback,ApiUser
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import os
import string
import random
from datetime import datetime
import requests

# home part
def home(request):
    if request.user.is_authenticated:
        user = User.objects.get(email = request.user.email)
        userimg = user.userimg
        return render(request,'book_review_app/home.html',{'form':Contactform,'userimg':userimg})
    if request.method == 'POST':
        form = Contactform(request.POST)
        name = request.POST['Name']
        email = request.POST['email']
        mess = request.POST['message']
        if form.is_valid():
            form.save()
            message = "Hi this is "+name+" .My query is "+mess+" .Please solve this query and share the solution via "+email+" ."
            send_mail('Query Message',message,'brsapp33@gmail.com',[email,],fail_silently=False)
            return redirect(reverse('home',messages.success(request,'Message sent successfully.')),permanent=True)
        else:
            return redirect(reverse('home',messages.error(request,'Oops an error occured! Please try again.')),permanent=True)
    return render(request,'book_review_app/home.html',{'form':Contactform})

# Register part
def register(request):
    if request.method == 'POST':
        form = Usercreateform(request.POST)
        if form.is_valid():
            recv_email = form.cleaned_data['email']
            recv_mobile_0 = request.POST['mobilenumber_0']
            recv_mobile_1 = request.POST['mobilenumber_1']
            recv_password = form.cleaned_data['password']
            recv_confirm_password = form.cleaned_data['confirm_password']

            number_prefix = "+"+ str(phonenumbers.country_code_for_region(recv_mobile_0))
            mobile = number_prefix + recv_mobile_1

            
            if recv_mobile_1[0] not in ['6','7','8','9']:
                return redirect(reverse('signup',messages.error(request,"Enter Valid Mobile Number.")),permnent=True)
            
            try:
                validate_international_phonenumber(mobile)
            except ValidationError:
                return redirect(reverse('signup',messages.error(request,"Invalid mobilenumber")),permanent=True)
            
            if recv_password != recv_confirm_password:
                return redirect(reverse('signup',messages.error(request,'Password and Confirm Password mismatched.')),permanent=True)

            user = form.save(commit=False)
            user.is_BRS_account = True
            user.is_active = False
            user.set_password(recv_password)
            user.save()
            return redirect('sendemail',recv_email,permanent=True)
        else:
            error = form.errors 
            return redirect(reverse('signup',messages.error(request,error)),permanent=True)
    return render(request,'book_review_app/register.html',{'form':Usercreateform})

#send email for account verification
def send_confirmation(request,email):
    if request.method == "GET":
        time = datetime.now()
        time_str = time.strftime("%Y")+time.strftime("%m")+time.strftime("%d")+time.strftime("%H")+time.strftime("%M")+time.strftime("%S")
        site = get_current_site(request)
        user = User.objects.get(email = email)
        body = urlsafe_base64_encode(force_bytes(email))
        timestamp = urlsafe_base64_encode(force_bytes(time_str))
        #print(request.get_host())
        #print(site.domain)
        mail_message = render_to_string('book_review_app/email.html',{'email':body,'name':user.username,'domain':site.domain,
                        'timestamp':timestamp,'scheme':request.scheme})
        try:
            send_mail('Account Confirmation','Account','brsapp33@gmail.com',[email,], html_message = mail_message,fail_silently=False)
            return redirect(reverse('signup',messages.success(request,'Check your email for account confirmation.')),permanent=True)
        except:
            return redirect(reverse('signup',messages.error(request,'An error occured. Make sure your device connected to the interet.')),permanent=True)

# confirm account verification
def verify_confirmation(request,email,time):
    if request.method == "GET":
        times = datetime.now()
        time_str = time_str =times.strftime("%Y")+times.strftime("%m")+times.strftime("%d")+times.strftime("%H")+times.strftime("%M")+times.strftime("%S")
        decrypt_time = urlsafe_base64_decode(force_str(time))
        
        if (int(time_str)-int(decrypt_time)) > 300:
            return redirect(reverse('home',messages.error(request,'Link expired.')),permanent=True)
        
        try:
            decrypt_email = urlsafe_base64_decode(force_str(email))
            str_decrypt_email = str(decrypt_email,encoding='utf-8')
            user = User.objects.get(email = str_decrypt_email)
        except:
            return redirect(reverse('home',messages.error(request,'Invalid User.')),permanent=True)
        
        if user.is_active == False:
            user.is_active = True
            user.save()
            return redirect(reverse('home',messages.success(request,'Account verification successfull.')),permanent=True)
        else:
            return redirect(reverse('home',messages.error(request,'Account Already verified.')),permanent=True)

# Login part
def login_user(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect(reverse('home',messages.error(request,"Account already signed in.")),permanent=True)
    if request.method == 'POST':
        form = Userloginform(request.POST)
        if form.is_valid():
            useremail = form.cleaned_data['email']
            userpwd = form.cleaned_data['password']
            next = request.POST['next']
            try:
                user = User.objects.get(email = useremail)
                if user.is_active:
                    person = authenticate(request,email = useremail,password = userpwd)
                    if person is not None:
                        login(request,person)
                        if next :
                            return redirect(next,permanent=True)
                        if user.is_superuser:
                            return redirect('/admin/',permanent=True)
                        else:
                            return redirect(reverse('home',messages.success(request,'Login successfully.')),permanent=True)
                    else:
                        messages.error(request,"Enter Valid Credentials.")
                else:
                    messages.error(request,'Sorry! This account is inactive.')
            except:
                messages.error(request,'Invalid User.')
        else:
            error = form.errors
            messages.error(request,error)
    form = Userloginform()
    form.order_fields(field_order=['email','password','captcha'])
    return render(request,'book_review_app/login.html',{'form':form})

# profile part
@login_required(login_url='signin')
def profile(request):
    user = User.objects.get(email = request.user.email)
    book = Book.objects.filter(user = request.user.id)
    return render(request,'book_review_app/profile.html',{'user':user,'books':len(book),'img':user.userimg})

# edit profile part
@login_required(login_url='signin')
def editprofile(request):
    if request.method == 'POST':
        form = Userupdateform(request.POST)
        if form.is_valid():
            recv_mobile_1 = request.POST['mobilenumber_1']
            recv_mobile_0 = request.POST['mobilenumber_0']
            recv_name = form.cleaned_data['username']
            
            number_prefix = "+"+ str(phonenumbers.country_code_for_region(recv_mobile_0))
            mobile = number_prefix + recv_mobile_1

            if recv_mobile_1[0] not in ['6','7','8','9']:
                return redirect(reverse('profileedit',messages.error(request,"Enter Valid Mobile Number.")),permanent=True)
            
            try:
                validate_international_phonenumber(mobile)
            except ValidationError:
                return redirect(reverse('profileedit',messages.error(request,"Invalid mobilenumber")),permanent=True)
            
            user = User.objects.get(email = request.user.email)
            user.username,user.mobilenumber = recv_name,mobile 
            user.save()
            return redirect(reverse('profile',messages.success(request,'Updated Successfully.')),permanent=True)
        else:
            error = form.errors 
            return redirect(reverse('profileedit',messages.error(request,error)),permanent=True)
    return render(request,'book_review_app/profile_edit.html',{'form':Userupdateform})

# profile image change part
@login_required(login_url='signin')
def profileimage(request):
    if request.method == 'POST':
        form = Userimageform(request.FILES)
        if form.is_valid():
            try:
                a = request.FILES['image']
            except:
                return redirect(reverse('profileimagechange',messages.error(request,'No image file selected.')),permanent=True) 
            user = User.objects.get(email = request.user.email)
            extension = os.path.splitext(request.FILES['image'].name)
            if extension[1] not in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG' ]:
                return redirect(reverse('profileimagechange',messages.error(request,'Invalid file format.')),permanent=True) 
            if user.userimg:
                try:
                    user.userimg.delete()
                    user.userimg = request.FILES['image']
                    user.save()
                except:
                    return redirect(reverse('profileimagechange',messages.error(request,'Error Occured Contact Admin.')),permanent=True)
            else:
                user.userimg = request.FILES['image']
                user.save()
            return redirect(reverse('profile',messages.success(request,'Profile picture successfully changed.')),permanent=True)
            
            
        elif not form.is_valid():
            error = form.errors
            messages.error(request,error)
    return render(request,'book_review_app/profileimg.html',{'form':Userimageform})

# Upload book review
@login_required(login_url='signin')
def book_review_upload(request):
    if request.method == 'POST':
        form = UserBookForm(request.POST or request.FILES)
        if form.is_valid():
            name = form.cleaned_data['bookname']
            author = form.cleaned_data['bookauthor']
            type = form.cleaned_data['booktype']
            try:
                imagefile = request.FILES['bookimg']
            except:
                return redirect(reverse('bookupload',messages.error(request,'No image file selected.')),permanent=True) 

            try:
                audiofile = request.FILES['bookfile']
            except:
                return redirect(reverse('bookupload',messages.error(request,'No audio file selected.')),permanent=True) 
            if imagefile.size > 1048576:
                return redirect(reverse('bookupload',messages.info(request,'Image File size must be less than 1mb.')),permanent=True)
            if audiofile.size > 3145728:
                return redirect(reverse('bookupload',messages.info(request,'Audio File size must be less than 3mb.')),permanent=True) 
           
            try:
                book = Book.objects.get(bookname = name,bookauthor = author,user = request.user.id,booktype = type )
                return redirect(reverse('bookupload',messages.error(request,'A file exist with the same identity')),permanent=True)
            except:
                Book.objects.create(user = User.objects.get(id = request.user.id),bookname = name, bookauthor = author,booktype = type,
                                        bookimg = imagefile, bookfile = audiofile)
                return redirect(reverse('bookupload',messages.success(request,'Upload successfully')),permanent=True)
        else:
            error = form.errors 
            return redirect(reverse('bookupload',messages.error(request,error)),permanent=True)

    return render(request,'book_review_app/reviewupload.html',{'form':UserBookForm})

# View Review collection
@login_required(login_url='signin')
def review_collection(request):
    book = Book.objects.all()
    if request.method == 'POST':
        query = request.POST['search']
        if Book.objects.filter(bookname__icontains = query):
            book = Book.objects.filter(bookname__icontains = query)
        elif Book.objects.filter(bookauthor__icontains = query):
            book = Book.objects.filter(bookauthor__icontains = query)
        elif Book.objects.filter(booktype__icontains = query):
            book = Book.objects.filter(booktype__icontains = query)
        else:
            return redirect(reverse('collection',messages.error(request,"No results found.")),permanent=True)
    
    page = Paginator(book,6)
    page_number = request.GET.get("page")
    
    try:
        page_obj = page.get_page(page_number)
    except:
        page_obj = page.get_page(1)
    
    #print("page_obj",page_obj)
    
    page_book = page_obj.object_list
    #print("page_book",page_book)
    
    if request.GET.get("order"):
        order = request.GET.get("order")
        if order == "oldest":
            page_book=sorted(page_book,key = lambda i : i.created_datetime)
        if order == "newest":
            page_book=sorted(page_book,key = lambda i : i.created_datetime,reverse=True)
        if order == "author":
            page_book=sorted(page_book,key = lambda i : i.bookauthor)
        if order == "review":
            page_book=sorted(page_book,key = lambda i : i.user.username)
        if order == "genere":
            page_book=sorted(page_book,key = lambda i : i.booktype)
        if order == "bookname":
            page_book=sorted(page_book,key = lambda i : i.bookname)
    
    return render(request,'book_review_app/collection.html',{'page_no':page_obj,'book':page_book})

# visit my review collection
@login_required(login_url='signin')
def my_reviews(request):
    user = User.objects.get(id = request.user.id)
    book = Book.objects.filter(user = user.id)
    if request.method == 'POST':
        query = request.POST['search']
        if Book.objects.filter(user = user.id,bookname__icontains = query):
            book = Book.objects.filter(user = user.id,bookname__icontains = query)
        elif Book.objects.filter(user = user.id,bookauthor__icontains = query):
            book = Book.objects.filter(user = user.id,bookauthor__icontains = query)
        elif Book.objects.filter(user = user.id,booktype__icontains = query):
            book = Book.objects.filter(user = user.id,booktype__icontains = query)
        else:
            return redirect(reverse('myreview',messages.error(request,"No results found.")),permanent=True)
    
    page = Paginator(book, 6)
    page_number = request.GET.get("page")
    try:
        page_obj = page.get_page(page_number)
    except:
        page_obj = page.get_page(1)
        
    return render(request,'book_review_app/mycollection.html',{'book':page_obj})


# Play audio and handle feedback
@login_required(login_url='signin')
def playaudio(request,name,author,reviewer,genere):
    user = User.objects.get(email = reviewer)
    book = Book.objects.get(bookname = name,bookauthor = author,user = user.id,booktype = genere )
    if request.method == "POST":
        form = Feedbackform(request.POST)
        if form.is_valid():
            Feedback.objects.create(user = user,book = book, feedback = request.POST['feedback'] )
            messages.success(request,'Feedback submitted successfully.')
        else:
            error = form.errors
            messages.error(request,error)
    
    return render(request,'book_review_app/play.html',{'data':book,'form':Feedbackform})

# edit upload book
@login_required(login_url='signin')
def book_review_edit(request,name,author,reviewer,genere):
    if request.method == 'POST':
        user = User.objects.get(email = reviewer)
        book = Book.objects.get(bookname = name,bookauthor = author,user = user.id,booktype = genere )
        form = UserBookForm(request.POST or request.FILES)
        if form.is_valid():
            book_name = form.cleaned_data['bookname']
            book_author = form.cleaned_data['bookauthor']
            type = form.cleaned_data['booktype']
            
            try:
                imagefile = request.FILES['bookimg']
                if imagefile.size > 1048576:
                    return redirect(reverse('bookupload',messages.info(request,'Image File size must be less than 1mb.')),permanent=True)
                else:
                    book.bookimg.delete()
                    book.bookimg = request.FILES['bookimg']
            except:
                pass

            try:
                audiofile = request.FILES['bookfile']
                if audiofile.size > 3145728:
                    return redirect(reverse('bookupload',messages.info(request,'Audio File size must be less than 3mb.')),permanent=True)
                else:
                    book.bookfile.delete()
                    book.bookfile = request.FILES['bookfile']
            except:
                pass
            try:
                book = Book.objects.get(bookname = book_name,bookauthor = book_author,user = request.user.id,booktype = type )
                return redirect(reverse('bookupload',messages.error(request,'A file exist with the same identity')),permanent=True)
            except:
                book.bookname,book.bookauthor,book.booktype = book_name,book_author,type    
                book.save()
                return redirect(reverse('myreview',messages.success(request,'Updated successfully')),permanent=True)
        else:
            error = form.errors 
            messages.error(request,error)
            
    return render(request,'book_review_app/reviewedit.html',{'form':UserBookForm})

# delete book review
@login_required(login_url='signin')
def book_review_delete(request,name,author,reviewer,genere):

    user = User.objects.get(email = reviewer)
    book = Book.objects.get(bookname = name,bookauthor = author,user = user.id,booktype = genere)
    try:
        book.bookfile.delete()
        book.bookimg.delete()
    except:
        messages.error(request,"Error occured contact the admin.")
    book.delete()
    return redirect(reverse('myreview',messages.success(request,"Deleted successfully")),permanent=True)

# show feedback
def show_feedback(request,name,author,reviewer,genere):
    if request.method == "GET":
        user = User.objects.get(email = reviewer)
        book = Book.objects.get(bookname = name,bookauthor = author,user = user.id,booktype = genere )
        feedback = Feedback.objects.filter(book=book.id)
        return render(request,'book_review_app/feedback.html',{'data':feedback})

# forgot password send email
def pwdchange_sendmsg(request):
    if request.method == "POST":
        time = datetime.now()
        time_str = time.strftime("%Y")+time.strftime("%m")+time.strftime("%d")+time.strftime("%H")+time.strftime("%M")+time.strftime("%S")
        timestamp = urlsafe_base64_encode(force_bytes(time_str))
        site = get_current_site(request)
        form = Emailform(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email = email)
            except:
                return redirect(reverse('pwdchangeemail',messages.error(request,'There is no account with this email. Please give your registered email')),permanent=True)
            if user.is_active == True:
                if user.is_BRS_account == True:
                    encrypted_email = urlsafe_base64_encode(force_bytes(email)) 
                    message =f'''Hello this is from Book Review System. Your can use the below link to change the password of your BRS account. link : '{request.scheme}://{site.domain}/forgotpassword/{encrypted_email}/{timestamp}/'. Don"t reply to this email.'''
                    send_mail('Password changing link',message,'brsapp33@gmail.com',[email],fail_silently=False)
                    return redirect(reverse('home',messages.info(request,'Check email and follow the link for changing your password.')),permanent=True)
                else:
                    messages.error(request,'Invalid Email. This email registered using third party.')
            else:
                messages.error(request,'De-active Account.')
    return render(request,'book_review_app/pwdemailmsg.html',{'form':Emailform})

# change password 
def pwdchange(request,value,time):
    times = datetime.now()
    time_str =times.strftime("%Y")+times.strftime("%m")+times.strftime("%d")+times.strftime("%H")+times.strftime("%M")+times.strftime("%S")
    decrypt_time = urlsafe_base64_decode(force_str(time))
    
    if (int(time_str)-int(decrypt_time)) > 300:
        return redirect(reverse('home',messages.error(request,'Link expired.')),permanent=True)
    
    decrypt_email =  urlsafe_base64_decode(force_str(value)) 
    
    try:
        str_decrypt_email = str(decrypt_email,encoding='utf-8')
    except:
        return redirect(reverse('home',messages.error(request,'Invalid Link.')),permanent=True)
    
    try:
        user = User.objects.get(email = str_decrypt_email)
    except:
        return redirect(reverse('home',messages.error(request,'Invalid User.')),permanent=True)
    
    if request.method == "POST":    
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            pwd = form.cleaned_data['password']
            confirm_pwd = form.cleaned_data['confirm_password']
            if pwd != confirm_pwd:
                return redirect(reverse('pwdchange',messages.error(request,'Password and Confirm Password mismatched.')),permanent=True)
            user.set_password(pwd)
            user.save()
            return redirect(reverse('home',messages.info(request,'password reset successful.')),permanent=True)
        else:
            error = form.errors
            return messages.error(request,error)
    
    return render(request,'book_review_app/pwdchange.html',{'form':PasswordChangeForm})

# send email verification link
def later_send_verification_email(request):
    if request.method == "POST":
        form = Emailform(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email = email)
            except:
                return redirect(reverse('sendemailverify',messages.error(request,'There is no account with this email. Please give your registered email')),permanent=True)
            if user.is_BRS_account == True:
                if user.is_active == False:
                    return redirect('sendemail',email,permanent=True)
                else:
                    messages.error(request,"Account already verified.")
            else:
                messages.error(request,"Invalid Email. This email registered using third party.")
    return render(request,'book_review_app/pwdemailmsg.html',{'form':Emailform})

@login_required(login_url = 'signin')
def getapi(request):
    if request.method == "POST":
        encode_email = urlsafe_base64_encode(force_bytes(request.user.email))
        key = ''.join(random.choices(string.ascii_lowercase +string.digits, k=35))
        apikey = f'{request.scheme}://{request.get_host()}/getbookreviews/{encode_email}/'
        try:
            usercreate = ApiUser.objects.create(user=request.user,token=key,app_name=request.POST['app_name'],app_type=request.POST['app_type'],is_valid=True)
            usercreate.save()
            return render(request,'book_review_app/showapi.html',{'url':apikey,'token':key,'name':request.user})
        except:
            return redirect(reverse('home',messages.info(request,"Already got Apikey")))
    if request.method == "GET":
        user = User.objects.get(email = request.user.email)
        if user.count < 2:
            return render(request,'book_review_app/apiform.html')
        else:
            return redirect(reverse('home',messages.info(request,"Sorry!, Maximum count reached.")))

@login_required(login_url="signin")
def forgotapi(request):
    if request.method == "GET":
        return render(request,'book_review_app/forgotapi.html',{'form':ForgotApiForm})
    if request.method == "POST":
        form = ForgotApiForm(request.POST)
        try:
            user = User.objects.get(email=request.user.email)
            apiuser = ApiUser.objects.get(user = user.id)
        except:
            return redirect(reverse('forgotapi',messages.error(request,'Invalid user')),permanent=True)
        if form.is_valid():
            password = form.cleaned_data['password']
            name = form.cleaned_data['app_name']
            type = form.cleaned_data['app_type']
            if (check_password(password,user.password)) and (apiuser.app_type == type) and (apiuser.app_name == name):
                encode_email = urlsafe_base64_encode(force_bytes(request.user.email))
                apikey = f'{request.scheme}://{request.get_host()}/getbookreviews/{encode_email}/'
                return render(request,'book_review_app/showapi.html',{'value':apiuser.token,'url':apikey,'username':user.username})
            else:
                return redirect(reverse('forgotapi',messages.error(request,'Invalid credentials')),permanent=True)
        else:
            return redirect(reverse('forgotapi',messages.error(request,form.errors)),permanent=True)

@login_required(login_url="signin")
def deleteapi(request):
    if request.method == "GET":
        return render(request,'book_review_app/deleteapi.html',{'form':ForgotApiForm})
    if request.method == "POST":
        form = ForgotApiForm(request.POST)
        try:
            user = User.objects.get(email=request.user.email)
            apiuser = ApiUser.objects.get(user = user.id)
        except:
            return redirect(reverse('forgotapi',messages.error(request,'Invalid user')),permanent=True)
        if form.is_valid():
            password = form.cleaned_data['password']
            name = form.cleaned_data['app_name']
            type = form.cleaned_data['app_type']
            if (check_password(password,user.password)) and (apiuser.app_type == type) and (apiuser.app_name == name):
                ApiUser.objects.get(user=user.id,app_name=name,app_type=type).delete()
                user.count += 1
                user.save()
                return redirect(reverse('home',messages.success(request,'API token deleted successfully.')),permanent=True)
            else:
                return redirect(reverse('deleteapi',messages.error(request,'Invalid user')),permanent=True)
        else:
            return redirect(reverse('deleteapi',messages.error(request,form.errors)),permanent=True)
                
    
def getpasform(request):
    if request.method == "GET":
        return render(request,'book_review_app/pasform.html')
    if request.method == "POST":
        formdata = {'nitrogen':request.POST.get("nitrogen"),'phosphorus':request.POST.get('phosphorus'),'potassium':request.POST.get('potassium'),
                    'temperature':request.POST.get('temperature'),'ph':request.POST.get('ph'),'rainfall':request.POST.get('rainfall'),
                    'humidity':request.POST.get('humidity')}
        response_data = requests.post("https://precision-agricultural-solution.onrender.com/getapicrop/c2FzaWd1cnV2aWduZXNoQGdtYWlsLmNvbQ/alewh2ohuqh8rqe2f01hiksm3nfgymvpafq/",data=formdata)
        if response_data.status_code == 200:
            json_response_data = response_data.json()
            return render(request,'book_review_app/pasresult.html',{"data":json_response_data})
        elif response_data.status_code == 400:
            return redirect(reverse('pasform',messages.error(request,"Bad request")),permanent=True)
        else:
            return redirect(reverse('pasform',messages.error(request,'Invalid form data')),permanent=True)
        
# merge account verify
def mergeaccountverify(request):
    if request.method == "GET":
        return render(request,'book_review_app/pwdemailmsg.html',{'form':Emailform})
    elif request.method == "POST":
        form = Emailform(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email = email)
            except:
                return redirect(reverse('merge',messages.error(request,'There is no account with this email. Please give your registered third party email')),permanent=True)
            if user.is_active == True:
                if user.is_BRS_account != True:
                    return render(request,'book_review_app/pwdchange.html',{'form':PasswordChangeForm,'key':'merge','email':email})
                else:
                    return redirect(reverse('merge',messages.error(request,'Not a third party account')),permanent=True)
            else:
                return redirect(reverse('merge',messages.error(request,'Account deactive. Please contact admin via contact form')),permanent=True)

# merge account success
def mergeaccount(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            pwd = form.cleaned_data['password']
            confirm_pwd = form.cleaned_data['confirm_password']
            if pwd != confirm_pwd:
                return redirect(reverse('merge',messages.error(request,'Password and Confirm Password mismatched.')),permanent=True)
            try:
                user = User.objects.get(email = email)
            except:
                return redirect(reverse('merge',messages.error(request,'There is no account with this email. Please give your registered third party email')),permanent=True)
            if user.is_active == True:
                if user.is_BRS_account != True:
                    user.is_BRS_account = True
                    user.set_password(pwd)
                    user.save()
                    return redirect(reverse('home',messages.success(request,'successfully merged')),permanent=True)
                else:
                    return redirect(reverse('merge',messages.error(request,'Not a third party account')),permanent=True)
            else:
                return redirect(reverse('merge',messages.error(request,'Account deactive. Please contact admin via contact form')),permanent=True)
  