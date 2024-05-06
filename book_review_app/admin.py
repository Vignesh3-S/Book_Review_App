from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.sessions.models import Session
from .models import User,Book,Contact,Feedback,ApiUser,APIFeedback

admin.site.register(Book)
admin.site.register(Contact)
admin.site.register(Session)
admin.site.register(Feedback)
admin.site.register(ApiUser)
admin.site.register(APIFeedback)

class CustomUserAdmin(UserAdmin):
    admin.site.site_header = "Book Review Administration"
    model = User
    list_display = ("username","email","last_login","is_active")
    list_filter = ("is_staff", "is_active","is_superuser","email",)
    fieldsets = (
        ("User Details", {"fields": ("username","mobilenumber","userimg")}),
        ("Authentiction Details", {"fields": ("email","password")}),
        ("Permissions", {"fields": ("is_staff", "is_active","is_superuser", "is_BRS_account", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("date_joined","date_modified","last_login")}),
        ("API information", {"fields": ("count",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username","email","mobilenumber", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions","is_BRS_account"
            )}
        ),
    )
    readonly_fields = ("date_modified","date_joined","last_login",)
    search_fields = ("email","mobilenumber",)
    ordering = ("date_joined",)

admin.site.register(User, CustomUserAdmin)
