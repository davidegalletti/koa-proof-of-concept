from django import forms
from django.forms.widgets import RadioSelect

class UploadFileForm(forms.Form):
    file  = forms.FileField(label='Select a file')
    
class ImportChoice(forms.Form):
    HOW_TO_IMPORT = [['0','Update if URI exists, create if URI is empty or non existent'],['1','Always create new records']]
    how_to_import = forms.ChoiceField( widget=RadioSelect(), choices=HOW_TO_IMPORT, label="How to import (it applies to each SimpleEntity)")
    uploaded_file_id = forms.CharField(widget=forms.HiddenInput())
    new_uploaded_file_relpath = forms.CharField(widget=forms.HiddenInput())
class ImportChoiceNothingOnDB(forms.Form):
    HOW_TO_IMPORT = [['1','Always create new records']]
    how_to_import = forms.ChoiceField( widget=RadioSelect(), choices=HOW_TO_IMPORT)
    uploaded_file_id = forms.CharField(widget=forms.HiddenInput())
    new_uploaded_file_relpath = forms.CharField(widget=forms.HiddenInput())
