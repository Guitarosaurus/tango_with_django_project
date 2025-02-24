from django import forms
from rango.models import Page, Category, UserProfile
from django.contrib.auth.models import User

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=Category.NAME_MAX_LENGTH, 
                           help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial = 0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    # An inline class to provide additional info on the form
    class Meta:
        # provide association between ModelForm and a model
        model = Category
        fields = ('name', )

class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=Page.TITLE_MAX_LENGTH,
                            help_text="Please enter the title of the page")
    url = forms.URLField(max_length=Page.URL_MAX_LENGTH,
                         help_text="Please enter the URL of the page")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        # provide association between the ModelForm and model
        model = Page

        # Specify which field to exclude 
        # Could have also specified which field to include
        exclude = ('category', )

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # If URL is not empty and doesnt start with 'http://' then prepend it
        if url and not url.startswith('http://') and not url.startswith('https://'):
            url = f'http://{url}'
            cleaned_data['url'] = url
        
        return cleaned_data
    
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password',)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture', )
