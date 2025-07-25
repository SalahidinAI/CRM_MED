from .models import *
from modeltranslation.translator import TranslationOptions, register


@register(Department)
class DepartmentTranslationOptions(TranslationOptions):
    fields = ('department_name',)


@register(JobTitle)
class JobTitleTranslationOptions(TranslationOptions):
    fields = ('job_title',)


@register(ServiceType)
class ServiceTypeTranslationOptions(TranslationOptions):
    fields = ('type',)
