import logging

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags

from .base_forms import BaseForm

###
logger = logging.getLogger('django')
###

class ContactForm(BaseForm):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200, required=False)
    message = forms.CharField(
        required=True,
        max_length=2000,
        widget=forms.Textarea(attrs={
            'placeholder':'',
            'role':'textbox',
            'rows':8
        })
    )

    def send_email(self):
        """
        Send email from the submitted contact form.

        Workflow:
        1. Construct email subject and body
        2. Use Django's send_mail function
        3. Handle potential email sending errors
        """
        # Construct the email subject
        subject = f"Contact Form Submission: {self.cleaned_data.get('subject', 'No Subject')}"

        # Construct the email body with additional context
        body = f"""
        Contact Form Submission Details:

        Name: {self.cleaned_data['name']}
        Email: {self.cleaned_data['email']}

        Message:
        {self.cleaned_data['message']}

        ---
        This is an automated email from the website contact form.
        """

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=self.cleaned_data['email'],  # Sender's email
                recipient_list=[settings.CONTACT_EMAIL[1]],  # Destination email
                fail_silently=False,  # Raise exceptions for debugging
            )
            return True
        except Exception as e:
            # Log the error for further investigation
            logger.error(f"Email sending failed: {e}")
            return False

class SubmitFeedbackForm(BaseForm):
    feedback = forms.CharField(
        label=None,
        max_length=500,
        widget=forms.Textarea(attrs={
            'placeholder': 'What would you like us to know?',
            'role':'textbox',
            'rows':'5'
        })
    )
    sent_by = forms.CharField()
    page = forms.URLField()

    def send_email(self):
        """
        Send email from the submitted contact form.

        Workflow:
        1. Construct email subject and body
        2. Use Django's send_mail function
        3. Handle potential email sending errors
        """
        # Construct the email subject
        subject = f"Feedback Form Submission:"
        # Construct the email body with additional context
        body = f"""
           Feedback Form Submission Details:
           {strip_tags(self.cleaned_data['feedback'])}
           ---
           Submitted by {self.cleaned_data['sent_by']}
           from {self.cleaned_data['page']}
           using the website feedback form.
           """
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.CONTACT_EMAIL[1],
                recipient_list=[settings.CONTACT_EMAIL[1]],
                fail_silently=False,  # Raise exceptions for debugging
            )
            return True
        except Exception as e:
            # Log the error for further investigation
            logger.error(f"Email sending failed: {e}")
            return False