from django import forms
from .models import Post, Comments


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        text = self.cleaned_data['text']
        if text == '':
            raise forms.ValidationError('Поле не дожно быть пeeустым')
        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('text',)
