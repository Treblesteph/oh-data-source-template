from django import forms


class UploadFileForm(forms.Form):
    print('making uploader')
    title = forms.CharField(max_length=50)
    file = forms.FileField(
        label='Select file',
        help_text='please select your twitter archive'
        )
