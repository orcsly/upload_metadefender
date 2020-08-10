from django import forms

from .metadefender import scan_file_sync


class FileFieldForm(forms.Form):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    def clean_files(self):
        files = self.files.getlist('files')
        for file in files:
            results, msg = scan_file_sync(file.name, file.open())
            print(results)
            if msg != 'Success' or results['scan_results']['scan_all_result_a'] == 'Infected':
                raise forms.ValidationError('Virus found - {} - {}'.format(results['scan_results']['scan_all_result_a'],
                                                                         results['scan_results']['total_detected_avs']))
        return files
