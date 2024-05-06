"""book_review_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.home,name = "home"),
    path('userregister/',views.register,name = "signup"),
    path('userlogin/',views.login_user,name = "signin"),
    path('userprofile/',views.profile,name = "profile"),
    path('bookupload/',views.book_review_upload,name = "bookupload"),
    path('bookedit/<str:name>/<str:author>/<str:reviewer>/<str:genere>/',views.book_review_edit,name = "editbook"),
    path('deletbook/<str:name>/<str:author>/<str:reviewer>/<str:genere>/',views.book_review_delete,name = "deletebook"),
    path('bookcollection/',views.review_collection,name = "collection"),
    path('mybookreviews/',views.my_reviews,name = "myreview"),
    path('verify/<str:email>/<str:time>/',views.verify_confirmation,name = "confirmemail"),
    path('sendconfirm/<email>/',views.send_confirmation,name = "sendemail"),
    path('useredit/',views.editprofile,name = 'profileedit'),
    path('viewfeedback/<str:name>/<str:author>/<str:reviewer>/<str:genere>/',views.show_feedback,name = 'viewfeedback'),
    path('userchangeimg/',views.profileimage,name = "profileimagechange"),
    path('play/<str:name>/<str:author>/<str:reviewer>/<str:genere>/',views.playaudio,name = "audioplay"),
    path('forgotpasswordemail/',views.pwdchange_sendmsg,name="pwdchangeemail"),
    path('forgotpassword/<str:value>/<str:time>/',views.pwdchange,name="changepwd"),
    path('verificationemail/',views.later_send_verification_email,name="sendemailverify"),
    path('logout/',auth_views.LogoutView.as_view(),name = "logout"),
    path('getapi/',views.getapi,name = "getapi"),
    path('forgotapi/',views.forgotapi,name = "forgotapi"),
    path('deleteapi/',views.deleteapi,name = "deleteapi"),
    path('pasform/',views.getpasform,name = "pasform"),
    path('mergeaccount/',views.mergeaccountverify,name = "merge"),
    path('mergeaccountsuccess/',views.mergeaccount,name = "mergesuccess"),
]
