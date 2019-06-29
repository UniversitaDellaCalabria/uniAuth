import json

from django.contrib import admin
from django.contrib import messages
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _

from . models import (AgreementRecord,
                      MetadataStore,
                      ServiceProvider)


@admin.register(AgreementRecord)
class AgreementRecordAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'sp_entity_id',
                    'created')
    readonly_fields = ('attrs', 'sp_entity_id', 'user')


@admin.register(MetadataStore)
class MetadataStoreAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'type',
                    'is_valid',
                    'is_active',
                    'updated')
    list_filter = ('is_valid',
                   'is_active',
                   'updated')
    search_fields = ('name', 'url')
    readonly_fields = ('created', 'updated', 'is_valid',
                       'metadata_element_preview')

    fieldsets = (
                (None, {'fields': (('name', 'type'),
                                   ('url', 'file'),
                                   'kwargs',
                                   ('is_active', ),
                                   'is_valid',
                                   ('created', 'updated'),
                                   'metadata_element_preview'
                                   )}),
                )

    class Media:
        js = ('textarea_autosize.js',)
    
    def metadata_element_preview(self, obj):
        dumps = json.dumps(obj.as_pysaml2_mdstore_row(),
                           indent=4)
        return  mark_safe(dumps.replace('\n', '<br>').replace('\s', '&nbsp'))
    metadata_element_preview.short_description = 'Metadata element preview'

    def save_model(self, request, obj, form, change):
        res = False
        msg = ''
        try:
            json.dumps(obj.as_pysaml2_mdstore_row())
            res = obj.validate()
            super(MetadataStoreAdmin, self).save_model(request, obj, form, change)
        except Exception as excp:
            obj.is_valid = False
            obj.save()
            msg = str(excp)
            
        if not res:
            messages.set_level(request, messages.ERROR)
            _msg = _("Storage not valid, if 'mdq' at least a "
                     "valid url must be inserted. "
                     "If local: at least a file or a valid path")
            if msg: _msg = _msg + '. ' + msg
            messages.add_message(request, messages.ERROR, _msg)

@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('display_name',
                    'agreement_screen',
                    'agreement_message',
                    'signing_algorithm',
                    'digest_algorithm',
                    'encrypt_saml_responses',
                    'is_active',
                    'updated')
    list_filter = ('created',
                   'signing_algorithm',
                   'digest_algorithm',
                   'encrypt_saml_responses',
                   'is_active',
                   'updated')
    search_fields = ('entity_id', 'display_name', 'metadata_url')
    readonly_fields = ('created', 'updated', 'as_idpspconfig_dict_element_html')

    fieldsets = (
                (None, {'fields': (('entity_id', 'display_name',),
                                   ('metadata_url',),
                                   ('signing_algorithm', 'digest_algorithm', 'encrypt_saml_responses'),
                                   ('is_active',),
                                   )}),
                (_('Agreement and Description'), {'fields': (('agreement_screen', 'agreement_consent_form',),
                                                             ('agreement_message', 'description'),
                                                            ),
                                                  'classes':('collapse',),
                                                  }),
                (_('Attributes'), {'fields': (
                                            ('attribute_processor',),
                                            ('attribute_mapping',),
                                           ),
                                    }),
                (_('Attributes preview'), {'fields': (
                                                        ('as_idpspconfig_dict_element_html',),
                                                     ),
                                           'classes': ('collapse',),
                                            }),
                (None, {'fields': (('created', 'updated'),)})
                )

    class Media:
        js = ('textarea_autosize.js',)

    def as_idpspconfig_dict_element_html(self, obj):
        return  mark_safe(json.dumps(obj.as_idpspconfig_dict_element(),
                                     indent=4).replace('\n', '<br>').replace('\s', '&nbsp'))
    as_idpspconfig_dict_element_html.short_description = 'SP config preview'

    def save_model(self, request, obj, form, change):
        try:
            obj.validate()
            super(ServiceProviderAdmin, self).save_model(request, obj, form, change)
        except Exception as e:
            messages.set_level(request, messages.ERROR)
            msg = _("AttributeProcessor or Attribute mapping "
                    "is not valid: {}").format(e)
            messages.add_message(request, messages.ERROR, msg)
        
