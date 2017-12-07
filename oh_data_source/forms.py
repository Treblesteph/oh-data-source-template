from django import forms


class UploadFileForm(forms.Form):
    print('making uploader')
    file = forms.FileField(
        label='Select file',
        help_text='please select your twitter archive'
        )
