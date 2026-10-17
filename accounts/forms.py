from django.contrib.auth.forms import UserCreationForm
from django import forms
from . models import User, Address

class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username','first_name','last_name','email','phone')

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','email','phone')

    def __init__(self, *args, **kwargs):
    
            super().__init__(*args, **kwargs)
    
            for field in self.fields.values():
                field.widget.attrs["class"] = "form-control"    


class AddressForm(forms.ModelForm):

    class Meta:
          model = Address
          fields = ('full_name','phone','address_line','city','state','pincode')
        
    def __init__(self, *args, **kwargs):
         
                super().__init__(*args, **kwargs)
         
                for field in self.fields.values():
                     field.widget.attrs["class"] = "form-control"    
     