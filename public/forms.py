from django import forms

class ContactForm(forms.Form):
    template = 'public/contact_form.html'
    email_template = 'public/email.txt'

    name = forms.CharField(required=False)
    mail = forms.CharField()
    phone = forms.CharField(required=False)
    message = forms.CharField(help_text="Viestisi...")

    def clean(self):
        r = super(ContactForm, self).clean()
        if 'mail' in r:
            r['email'] = r['mail']
        return r
