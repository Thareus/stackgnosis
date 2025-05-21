from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        data = form.cleaned_data
        email = data.get("email")
        if not email:
            raise ValueError("Email is required for registration.")
        user_email(user, email)
        if "password1" in data:
            user.set_password(data["password1"])
        elif "password" in data:
            user.set_password(data["password"])
        else:
            user.set_unusable_password()
        if commit:
            user.save()
        return user

    def login(self, request, user):
        super().login(request, user)