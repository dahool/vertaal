from django.db.models import fields
from common.utils.slug import slugify

class AutoSlugField(fields.SlugField):
    def __init__(self, prepopulate_from, force_update = False, *args, **kwargs):
        self.prepopulate_from = prepopulate_from
        self.force_update = force_update
        super(AutoSlugField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if self.prepopulate_from:
            value = slugify(model_instance, self, getattr(model_instance, self.prepopulate_from), self.force_update)
        else:
            value = super(AutoSlugField, self).pre_save(model_instance, add)
        setattr(model_instance, self.attname, value)
        return value