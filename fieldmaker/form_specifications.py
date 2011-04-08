from django import forms
from django.utils.datastructures import SortedDict

from resource import field_registry

class FormSpecification(object):
    version = 'base.1'
    example = {'form_specification':version,
               'fields': [
                   {'name':'email',
                    'field':'EmailField',
                    'field_spec':{'max_length':'128'},
                    'widget':'TextInput',
                    'widget_spec':{},}
               ]}
    
    def create_form(self, data):
        class GeneratedForm(forms.Form):
            pass
            
        GeneratedForm.base_fields = self.get_fields(data)
        return GeneratedForm
    
    def get_fields(self, data):
        field_dict = SortedDict()
        for field_def in data['fields']:
            #fetch the makers
            field_maker = field_registry.fields[field_def['field']]
            widget_maker = field_registry.widgets[field_def['widget']]
            
            widget = widget_maker.create_widget(field_def['widget_spec'])
            field_kwargs = dict(field_def['field_spec'])
            field_kwargs['widget'] = widget
            field = field_maker.create_field(field_kwargs)
            
            field_dict[field_def['name']] = field
        return field_dict
    
    def extend_form(self, form, data):
        form.fields.update(self.get_fields(data))
    
    def bound_field_form_set_to_data(self, formset):
        data = {'form_specification':self.version,
                'fields':list(),}
        assert formset.is_valid()
        for form in formset:
            field = {'name':form.cleaned_data['name'],
                     'field':form.cleaned_data['field'],
                     'field_spec':form.field_form.cleaned_data,
                     'widget':form.cleaned_data['widget'],
                     'widget_spec':form.widget_form.cleaned_data,}
            data['fields'].append(field)
        return data
    
    def data_to_field_form_set_initial(self, data):
        return data['fields']

field_registry.register_form_specification(FormSpecification.version, FormSpecification())
