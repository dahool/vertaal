from django import forms

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':4, 'cols':30}))
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)