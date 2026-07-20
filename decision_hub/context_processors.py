from .forms import ProjectForm


def project_form_context(request):
    """
    Provides global_project_form to all templates so the 'Create New Project' modal
    can be opened from anywhere in the application header.
    """
    return {
        "global_project_form": ProjectForm()
    }
