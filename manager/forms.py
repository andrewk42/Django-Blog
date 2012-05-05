from django.forms import ModelForm
from manager.models import Settings

class SettingsForm(ModelForm):
    class Meta:
        model = Settings

class ValidSettings(Exception):
    def __str__(self):
        return "The processed form is valid and has been saved"

def formhandlerSettings(request):
    # SettingsForm processing
    if request.method == 'POST':
        # Create a form/new model entry from POST data
        settings_form = SettingsForm(request.POST)

        if settings_form.is_valid():
            settings_form.save()

            # This avoids duplicate form submissions
            raise ValidSettings

    # New, unbound form case
    else:
        # Override the default values in the model, which are really meant for testing
        settings = Settings.objects.get_or_create(id=1)[0]
        settings_form = SettingsForm(instance=settings)

    return settings_form
