from django.contrib import admin
from .models import *
from modeltranslation.admin import TranslationAdmin


class GeneralMedia:
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Department)
class DepartmentAdmin(TranslationAdmin, GeneralMedia):
    pass


@admin.register(JobTitle)
class JobTitleAdmin(TranslationAdmin, GeneralMedia):
    pass


@admin.register(ServiceType)
class ServiceTypeAdmin(TranslationAdmin, GeneralMedia):
    pass


admin.site.register(UserProfile)
admin.site.register(Admin)
admin.site.register(Receptionist)
admin.site.register(Room)
admin.site.register(Doctor)
admin.site.register(Patient)
