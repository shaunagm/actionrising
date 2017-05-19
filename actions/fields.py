from datetime import time

from django import forms
from django.forms.utils import to_current_timezone


class SlateChoiceField(forms.ModelMultipleChoiceField):
   def label_from_instance(self, obj):
        return obj.title


class LooseTimeField(forms.TimeField):
    # type=date doesn't work everywhere so we're falling back to parsing the
    # date with some loose input types

    input_formats = [
        "%H:%M",
        "%H %M",
        "%I:%M %p",
    ]


class SplitDateTimeWidget(forms.MultiWidget):
    """ copy for SplitDateTimeWidget with html5 types """
    supports_microseconds = False

    def __init__(self, attrs=None, date_format=None, time_format=None):
        attrs = attrs or {}
        date_attrs = attrs.copy()
        date_attrs['type'] = 'date'
        date_attrs['placeholder'] = 'YYYY-MM-DD'

        time_attrs = attrs.copy()
        time_attrs['type'] = 'time'
        time_attrs['placeholder'] = 'HH:MM AM'

        widgets = (
            forms.DateInput(attrs=date_attrs, format=date_format),
            forms.TimeInput(attrs=time_attrs),
        )
        super(SplitDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            value = to_current_timezone(value)
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]


class MidnightSplitDateTimeField(forms.SplitDateTimeField):
    """ slimmed down SplitDateTimeField replacing TimeField for LooseTimeField
    and replacing empty time with midnight """

    widget = SplitDateTimeWidget

    def __init__(self, input_date_formats=None, input_time_formats=None, *args, **kwargs):
        errors = self.default_error_messages.copy()
        fields = (
            forms.DateField(input_formats=input_date_formats,
                      error_messages={'invalid': errors['invalid_date']}),
            LooseTimeField(input_formats=input_time_formats, required=False,
                      error_messages={'invalid': errors['invalid_time']})
        )

        kwargs.setdefault('require_all_fields', False)

        # deliberately skipping immediate parent since it tries to the fields
        super(forms.SplitDateTimeField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            if not data_list[1]:
                data_list[1] = time()
        return super(MidnightSplitDateTimeField, self).compress(data_list)


