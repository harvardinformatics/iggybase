from wtforms import StringField, IntegerField, BooleanField, DateField, TextAreaField, FloatField, SelectField,\
    FileField, PasswordField, DecimalField


class IggybaseLookUpField(StringField):
    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
            del kwargs['title']
        else:
            self.title = None

        if 'iggybase_class' in kwargs:
            self.iggybase_class = 'lookupfield form-control-lookup ' + kwargs['iggybase_class']
            temp_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = 'lookupfield form-control-lookup'

        if kwargs['readonly']:
            self.iggybase_class = temp_class

        self.readonly = kwargs['readonly']
        del kwargs['readonly']

        super(IggybaseLookUpField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.readonly:
            kwargs.setdefault('readonly', True)
        else:
            kwargs.setdefault('data-toggle', "modal")

        kwargs['class'] = self.iggybase_class
        return super(IggybaseLookUpField, self).__call__(*args, **kwargs)


class IggybaseSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
            del kwargs['title']
        else:
            self.title = None

        if 'iggybase_class' in kwargs:
            self.iggybase_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = None

        self.readonly = kwargs['readonly']
        del kwargs['readonly']

        super(IggybaseSelectField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseSelectField, self).__call__(*args, **kwargs)


class IggybaseBooleanField(BooleanField):
    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
            del kwargs['title']
        else:
            self.title = None

        if 'iggybase_class' in kwargs:
            self.iggybase_class = 'boolean-field ' + kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = 'boolean-field'

        self.readonly = kwargs['readonly']
        del kwargs['readonly']

        super(IggybaseBooleanField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseBooleanField, self).__call__(*args, **kwargs)


class IggybaseDateField(DateField):
    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
            del kwargs['title']
        else:
            self.title = None

        if 'iggybase_class' in kwargs:
            self.iggybase_class = 'datepicker ' + kwargs['iggybase_class']
            temp_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = 'datepicker'

        if 'readonly' in kwargs:
            # remove datepicker for readonly
            self.iggybase_class = temp_class

        self.iggybase_class += ' date-field'

        self.readonly = kwargs['readonly']
        del kwargs['readonly']

        super(IggybaseDateField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseDateField, self).__call__(*args, **kwargs)


class IggybaseTextAreaField(TextAreaField):
    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
            del kwargs['title']
        else:
            self.title = None

        if 'iggybase_class' in kwargs:
            self.iggybase_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = None

        self.readonly = kwargs['readonly']
        del kwargs['readonly']

        super(IggybaseTextAreaField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseTextAreaField, self).__call__(*args, **kwargs)


class IggybaseFloatField(FloatField):
    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
            del kwargs['title']
        else:
            self.title = None

        if 'iggybase_class' in kwargs:
            self.iggybase_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = None

        self.readonly = kwargs['readonly']
        del kwargs['readonly']

        super(IggybaseFloatField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseFloatField, self).__call__(*args, **kwargs)


class IggybaseDecimalField(DecimalField):
    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
            del kwargs['title']
        else:
            self.title = None

        if 'iggybase_class' in kwargs:
            self.iggybase_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = None

        self.readonly = kwargs['readonly']
        del kwargs['readonly']

        super(IggybaseDecimalField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseDecimalField, self).__call__(*args, **kwargs)


class IggybaseIntegerField(IntegerField):
    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
            del kwargs['title']
        else:
            self.title = None

        if 'iggybase_class' in kwargs:
            self.iggybase_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = None

        self.readonly = kwargs['readonly']
        del kwargs['readonly']

        super(IggybaseIntegerField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseIntegerField, self).__call__(*args, **kwargs)


class IggybaseStringField(StringField):
    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
            del kwargs['title']
        else:
            self.title = None

        if 'iggybase_class' in kwargs:
            self.iggybase_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = None

        self.readonly = kwargs['readonly']
        del kwargs['readonly']

        super(IggybaseStringField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseStringField, self).__call__(*args, **kwargs)


class IggybaseFileField(FileField):
    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
            del kwargs['title']
        else:
            self.title = None

        if 'iggybase_class' in kwargs:
            self.iggybase_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = None

        self.readonly = kwargs['readonly']
        del kwargs['readonly']

        super(IggybaseFileField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        kwargs.setdefault('multiple', True)

        return super(IggybaseFileField, self).__call__(*args, **kwargs)


class IggybasePasswordField(PasswordField):
    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
            del kwargs['title']
        else:
            self.title = None

        if 'iggybase_class' in kwargs:
            self.iggybase_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = None

        self.readonly = kwargs['readonly']
        del kwargs['readonly']

        super(IggybasePasswordField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybasePasswordField, self).__call__(*args, **kwargs)
