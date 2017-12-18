from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='Select file',
        help_text='please select your twitter archive csv file'
        )
