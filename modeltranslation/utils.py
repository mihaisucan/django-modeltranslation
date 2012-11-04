# -*- coding: utf-8 -*-
from django.conf import global_settings
from django.utils.encoding import force_unicode
from django.utils.translation import get_language as _get_language
from django.utils.functional import lazy

from modeltranslation import settings as mt_settings


def get_language():
    """
    Return an active language code that is guaranteed to be in
    settings.LANGUAGES (Django does not seem to guarantee this for us).
    """
    lang = _get_language()
    if lang not in mt_settings.AVAILABLE_LANGUAGES and '-' in lang:
        lang = lang.split('-')[0]
    if lang in mt_settings.AVAILABLE_LANGUAGES:
        return lang
    return mt_settings.DEFAULT_LANGUAGE


def get_translation_fields(field_name, include_original=False):
    """
    Returns a list of localized fieldnames for a given field_name.
    """
    translation_fields = [build_localized_fieldname(
        field_name, l) for l in mt_settings.FIELD_LANGUAGES]
    if include_original:
        translation_fields.insert(0, field_name)
    return translation_fields


def build_localized_fieldname(field_name, lang):
    return str('%s_%s' % (field_name, lang.replace('-', '_')))


def _build_localized_verbose_name(verbose_name, lang):
    return u'%s [%s]' % (force_unicode(verbose_name), lang)
build_localized_verbose_name = lazy(_build_localized_verbose_name, unicode)


def _join_css_class(bits, offset):
    if ('-'.join(bits[-offset:]) in
            [l[0] for l in global_settings.LANGUAGES]):
        return '%s-%s' % ('_'.join(bits[:len(bits) - offset]),
                          '_'.join(bits[-offset:]))
    return ''


def build_css_class(localized_fieldname, prefix=''):
    """
    Returns a css class based on ``localized_fieldname`` which is easily
    splitable and capable of regionalized language codes.

    Takes an optional ``prefix`` which is prepended to the returned string.
    """
    bits = localized_fieldname.split('_')
    css_class = ''
    if bits[0] == '':
        return ''
    if len(bits) == 1:
        css_class = str(localized_fieldname)
    elif len(bits) == 2:
        # Fieldname without underscore and short language code
        # Examples:
        # 'foo_de' --> 'foo-de',
        # 'bar_en' --> 'bar-en'
        css_class = '-'.join(bits)
    elif len(bits) > 2:
        # Try regionalized language code
        # Examples:
        # 'foo_es_ar' --> 'foo-es_ar',
        # 'foo_bar_zh_tw' --> 'foo_bar-zh_tw'
        css_class = _join_css_class(bits, 2)
        if not css_class:
            # Try short language code
            # Examples:
            # 'foo_bar_de' --> 'foo_bar-de',
            # 'foo_bar_baz_de' --> 'foo_bar_baz-de'
            css_class = _join_css_class(bits, 1)
    return '%s-%s' % (prefix, css_class) if prefix else css_class
