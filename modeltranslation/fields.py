# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields import CharField, TextField
from django.db.models.fields.files import FileField, ImageField

from modeltranslation import settings as mt_settings
from modeltranslation.utils import (get_language, build_localized_fieldname,
                                    build_localized_verbose_name)


SUPPORTED_FIELDS = (CharField, TextField, FileField, ImageField,)


def create_translation_field(model, field_name, lang):
    """
    Translation field factory. Returns a ``TranslationField`` based on a
    fieldname and a language.

    The list of supported fields can be extended by defining a tuple of field
    names in the projects settings.py like this::

        MODELTRANSLATION_CUSTOM_FIELDS = ('MyField', 'MyOtherField',)

    If the class is neither a subclass of fields in ``SUPPORTED_FIELDS``, nor
    in ``CUSTOM_FIELDS`` an ``ImproperlyConfigured`` exception will be raised.
    """
    field = model._meta.get_field(field_name)
    cls_name = field.__class__.__name__
    if not (isinstance(field, SUPPORTED_FIELDS) or
            cls_name in mt_settings.CUSTOM_FIELDS):
        raise ImproperlyConfigured(
            '%s is not supported by modeltranslation.' % cls_name)
    translation_cls = field_factory(field.__class__)
    return translation_cls(translated_field=field, language=lang)


def field_factory(baseclass):
    class TranslationField(TranslationFieldBase, baseclass):
        pass
    return TranslationField


class TranslationFieldBase(object):
    """
    The translation field functions as a proxy to the original field which is
    wrapped.

    For every field defined in the model's ``TranslationOptions`` localized
    versions of that field are added to the model depending on the languages
    given in ``settings.LANGUAGES``.

    If for example there is a model ``News`` with a field ``title`` which is
    registered for translation and the ``settings.LANGUAGES`` contains the
    ``de`` and ``en`` languages, the fields ``title_de`` and ``title_en`` will
    be added to the model class. These fields are realized using this
    descriptor.

    The translation field needs to know which language it contains therefore
    that needs to be specified when the field is created.
    """
    def __init__(self, translated_field, language, *args, **kwargs):
        # Update the dict of this field with the content of the original one
        # This might be a bit radical?! Seems to work though...
        self.__dict__.update(translated_field.__dict__)
        self._post_init(translated_field, language)

    def _post_init(self, translated_field, language):
        """
        Common init for subclasses of TranslationFieldBase.
        """
        # Store the originally wrapped field for later
        self.translated_field = translated_field
        self.language = language

        # Translation are always optional (for now - maybe add some parameters
        # to the translation options for configuring this)
        self.null = True
        self.blank = True

        # Adjust the name of this field to reflect the language
        self.attname = build_localized_fieldname(
            self.translated_field.name, self.language)
        self.name = self.attname

        # Copy the verbose name and append a language suffix
        # (will show up e.g. in the admin).
        self.verbose_name = build_localized_verbose_name(
            translated_field.verbose_name, language)

    def get_prep_value(self, value):
        if value == '':
            value = None
        return self.translated_field.get_prep_value(value)

    def get_prep_lookup(self, lookup_type, value):
        return self.translated_field.get_prep_lookup(lookup_type, value)

    def to_python(self, value):
        return self.translated_field.to_python(value)

    def get_internal_type(self):
        return self.translated_field.get_internal_type()

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = '%s.%s' % (self.translated_field.__class__.__module__,
                                 self.translated_field.__class__.__name__)
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)

    def formfield(self, *args, **kwargs):
        """
        Preserves the widget of the translated field.
        """
        trans_formfield = self.translated_field.formfield(*args, **kwargs)
        defaults = {'widget': type(trans_formfield.widget)}
        defaults.update(kwargs)
        return super(TranslationFieldBase, self).formfield(*args, **defaults)


class TranslationFieldDescriptor(object):
    """
    A descriptor used for the original field (e.g. ``title``).
    """
    def __init__(self, name, initial_val='', fallback_value=None):
        """
        The ``name`` is the name of the field (which is not available in the
        descriptor by default - this is Python behaviour).
        """
        self.name = name
        self.val = initial_val
        self.fallback_value = fallback_value

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def __get__(self, instance, owner):
        if not instance:
            raise ValueError(
                "Translation field '%s' can only be accessed via an instance "
                "not via a class." % self.name)
        lang = get_language()

        # If current language is the default language, simply return the
        # fields standard value.
        if lang == mt_settings.DEFAULT_LANGUAGE:
            #print ('If current language is the default language, simply '
            #       'return the fields standard value (lang: %s).' % lang)
            return instance.__dict__[self.name]

        loc_field_name = build_localized_fieldname(self.name, lang)
        if hasattr(instance, loc_field_name):
            if getattr(instance, loc_field_name):
                # Return current language's translation field value
                # (e.g. ``title_de``).
                #print 'Return current languages translation field value'
                return getattr(instance, loc_field_name)
            elif self.fallback_value is None:
                # Return standard field value
                #print 'Return standard field value (loc_field_name: %s)' % (
                #    loc_field_name)
                return instance.__dict__[self.name]
            else:
                # Return fallback field value
                #print 'Return fallback field value'
                return self.fallback_value
