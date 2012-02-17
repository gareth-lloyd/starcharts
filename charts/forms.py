from django import forms
from datetime import datetime, date
from charts.models import CheckIn, Chart, TRACKING, TARGETED
from magicdate import magicdate

class DefaultToOneFloatField(forms.FloatField):
    def to_python(self, value):
        if not value:
            print 'default'
            self.defaulted = True
            value = 1.0
        else:
            self.defaulted = False
        return super(DefaultToOneFloatField, self).to_python(value)

class DateFromStringField(forms.DateField):

    def to_python(self, value):
        if value: 
            try:
                result = magicdate(value)
                if isinstance(result, datetime):
                    return result.date()
                else:
                    return result
            except Exception:
                raise ValueError()
        elif not value:
            # default
            return date.today()
        else:
            return super(DateFromStringField, self).to_python(value)

class AddCheckInForm(forms.ModelForm):
    number = DefaultToOneFloatField()
    when = DateFromStringField()

    class Meta:
        model = CheckIn
        exclude = ('created', 'chart')

    def clean(self):
        data = self.cleaned_data
        chart = self.instance.chart
        if chart.variable_achievements:
            if self.fields['number'].defaulted:
                raise forms.ValidationError('Must supply a number')
        else:
            data['number'] = 1
        return data

class AddChartForm(forms.ModelForm):
    def clean(self):
        target = self.cleaned_data['target']
        target_operator = self.cleaned_data['target_operator']
        accumulation_period = self.cleaned_data['accumulation_period']

        if target or target_operator:
            if not (target and target_operator):
                raise forms.ValidationError('Target and target operator must be specified')

        return self.cleaned_data

    class Meta:
        model = Chart
        exclude = ('created', 'user', )
