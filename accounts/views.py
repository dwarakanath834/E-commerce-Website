from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import AccountDetailsForm, RegistrationForm


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your ShopEase account is ready.")
        next_url = request.POST.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(next_url)
        if request.session.get("pending_cart_item"):
            return redirect("resume_pending_cart")
        return redirect("home")
    return render(request, "accounts/register.html", {"form": form, "next": request.GET.get("next", "")})


@login_required
def profile(request):
    form = AccountDetailsForm(request.POST or None, instance=request.user, profile=request.user.profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your account details have been updated.")
        return redirect("profile")
    return render(request, "accounts/profile.html", {"form": form})