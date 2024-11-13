from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from smtplib import SMTPException
from django.core.mail import send_mail
from smtplib import SMTPException
# Affir6matib3#ve

import requests
# Create your views here.

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Create user
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                phone_number = form.cleaned_data['phone_number']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                username = email.split("@")[0]
                
                user = Account.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    password=password
                )
                user.phone_number = phone_number
                user.save()

                # Email Configuration
                smtp_host = 'smtp.gmail.com'
                smtp_port = 587
                smtp_username = 'powellhabwe@gmail.com'
                smtp_password = 'fpbwpiaxfhkndmmm' 

                # Prepare verification email
                current_site = get_current_site(request)
                mail_subject = 'Please activate your account'
                message = render_to_string('accounts/account_verification_email.html', {
                    'user': user,
                    'domain': current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })

                try:
                    # Create MIME message
                    msg = MIMEMultipart()
                    msg['From'] = smtp_username
                    msg['To'] = email
                    msg['Subject'] = mail_subject

                    # Add message body
                    msg.attach(MIMEText(message, 'html'))

                    # Create SMTP session
                    server = smtplib.SMTP(smtp_host, smtp_port)
                    server.starttls()  # Enable TLS
                    server.login(smtp_username, smtp_password)

                    # Send email
                    server.send_message(msg)
                    server.quit()

                    messages.success(request, 'Registration successful. Please check your email for verification.')
                    return redirect('/accounts/login/?command=verification&email='+email)

                except Exception as e:
                    print(f"Failed to send email: {str(e)}")
                    messages.error(request, 'Failed to send verification email. Please contact support.')
                    user.delete()  # Remove user if email fails
                    return redirect('register')

            except Exception as e:
                print(f"Registration error: {str(e)}")
                messages.error(request, 'An error occurred during registration. Please try again.')
                return redirect('register')
    else:
        form = RegistrationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        current_user = request.user

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('/')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')


@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            try:
                user = Account.objects.get(email__exact=email)

                # Email Configuration
                smtp_host = 'smtp.gmail.com'
                smtp_port = 587
                smtp_username = 'powellhabwe@gmail.com'
                smtp_password = 'fpbwpiaxfhkndmmm'

                # Prepare reset password email
                current_site = get_current_site(request)
                mail_subject = 'Reset Your Password'
                message = render_to_string('accounts/reset_password_email.html', {
                    'user': user,
                    'domain': current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })

                try:
                    # Create MIME message
                    msg = MIMEMultipart()
                    msg['From'] = smtp_username
                    msg['To'] = email
                    msg['Subject'] = mail_subject

                    # Add message body
                    msg.attach(MIMEText(message, 'html'))

                    # Create SMTP session
                    server = smtplib.SMTP(smtp_host, smtp_port)
                    server.starttls()  # Enable TLS
                    server.login(smtp_username, smtp_password)

                    # Send email
                    server.send_message(msg)
                    server.quit()

                    messages.success(request, 'Password reset email has been sent to your email address.')
                    return redirect('login')

                except Exception as e:
                    print(f"Failed to send password reset email: {str(e)}")
                    messages.error(request, 'Failed to send password reset email. Please try again later.')
                    return redirect('forgotPassword')

            except Exception as e:
                print(f"Error in forgot password process: {str(e)}")
                messages.error(request, 'An error occurred. Please try again.')
                return redirect('forgotPassword')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist) as e:
        print(f"Error validating password reset token: {str(e)}")
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has expired or is invalid!')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            try:
                uid = request.session.get('uid')
                user = Account.objects.get(pk=uid)
                user.set_password(password)
                user.save()
                messages.success(request, 'Password reset successful')
                return redirect('login')
            except Exception as e:
                print(f"Error resetting password: {str(e)}")
                messages.error(request, 'An error occurred. Please try again.')
                return redirect('resetPassword')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        try:
            user = Account.objects.get(username__exact=request.user.username)

            if new_password == confirm_password:
                success = user.check_password(current_password)
                if success:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Password updated successfully. Please login with your new password.')
                    auth.logout(request)
                    return redirect('login')
                else:
                    messages.error(request, 'Current password is incorrect')
                    return redirect('change_password')
            else:
                messages.error(request, 'Passwords do not match!')
                return redirect('change_password')
        except Exception as e:
            print(f"Error changing password: {str(e)}")
            messages.error(request, 'An error occurred. Please try again.')
            return redirect('change_password')

    return render(request, 'accounts/change_password.html')