from wtforms import StringField, IntegerField, BooleanField, DateField, TextAreaField, FloatField, SelectField,\
    FileField, PasswordField


class IggybaseLookUpField(StringField):
    def __init__(self, *args, **kwargs):
        if 'iggybase_class' in kwargs:
            self.iggybase_class = 'lookupfield form-control-lookup ' + kwargs['iggybase_class']
            temp_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = 'lookupfield form-control-lookup'

        if 'readonly' in kwargs:
            self.readonly = kwargs['readonly']
            del kwargs['readonly']
            # remove lookup for readonly
            self.iggybase_class = temp_class
        else:
            self.readonly = False

        super(IggybaseLookUpField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        kwargs['class'] = self.iggybase_class
        return super(IggybaseLookUpField, self).__call__(*args, **kwargs)


class IggybaseSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        if 'iggybase_class' in kwargs:
            self.iggybase_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = None

        if 'readonly' in kwargs:
            self.readonly = kwargs['readonly']
            del kwargs['readonly']
        else:
            self.readonly = False

        super(IggybaseSelectField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseSelectField, self).__call__(*args, **kwargs)


class IggybaseBooleanField(BooleanField):
    def __init__(self, *args, **kwargs):
        if 'iggybase_class' in kwargs:
            self.iggybase_class = 'boolean-field ' + kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = 'boolean-field'

        if 'readonly' in kwargs:
            self.readonly = kwargs['readonly']
            del kwargs['readonly']
        else:
            self.readonly = False

        super(IggybaseBooleanField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseBooleanField, self).__call__(*args, **kwargs)


class IggybaseDateField(DateField):
    def __init__(self, *args, **kwargs):
        if 'iggybase_class' in kwargs:
            self.iggybase_class = 'datepicker-field ' + kwargs['iggybase_class']
            temp_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = 'datepicker-field'

        if 'readonly' in kwargs:
            self.readonly = kwargs['readonly']
            del kwargs['readonly']
            # remove datepicker for readonly
            self.iggybase_class = temp_class
        else:
            self.readonly = False

        super(IggybaseDateField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseDateField, self).__call__(*args, **kwargs)


class IggybaseTextAreaField(TextAreaField):
    def __init__(self, *args, **kwargs):
        if 'iggybase_class' in kwargs:
            self.iggybase_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = None

        if 'readonly' in kwargs:
            self.readonly = kwargs['readonly']
            del kwargs['readonly']
        else:
            self.readonly = False

        super(IggybaseTextAreaField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseTextAreaField, self).__call__(*args, **kwargs)


class IggybaseFloatField(FloatField):
    def __init__(self, *args, **kwargs):
        if 'iggybase_class' in kwargs:
            self.iggybase_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = None

        if 'readonly' in kwargs:
            self.readonly = kwargs['readonly']
            del kwargs['readonly']
        else:
            self.readonly = False

        super(IggybaseFloatField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseFloatField, self).__call__(*args, **kwargs)


class IggybaseIntegerField(IntegerField):
    def __init__(self, *args, **kwargs):
        if 'iggybase_class' in kwargs:
            self.iggybase_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = None

        if 'readonly' in kwargs:
            self.readonly = kwargs['readonly']
            del kwargs['readonly']
        else:
            self.readonly = False

        super(IggybaseIntegerField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseIntegerField, self).__call__(*args, **kwargs)


class IggybaseStringField(StringField):
    def __init__(self, *args, **kwargs):
        if 'iggybase_class' in kwargs:
            self.iggybase_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = None

        if 'readonly' in kwargs:
            self.readonly = kwargs['readonly']
            del kwargs['readonly']
        else:
            self.readonly = False

        super(IggybaseStringField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseStringField, self).__call__(*args, **kwargs)


class IggybaseFileField(FileField):
    def __init__(self, *args, **kwargs):
        if 'iggybase_class' in kwargs:
            self.iggybase_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = None

        if 'readonly' in kwargs:
            self.readonly = kwargs['readonly']
            del kwargs['readonly']
        else:
            self.readonly = False

        super(IggybaseFileField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybaseFileField, self).__call__(*args, **kwargs)


class IggybasePasswordField(PasswordField):
    def __init__(self, *args, **kwargs):
        if 'iggybase_class' in kwargs:
            self.iggybase_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = None

        if 'readonly' in kwargs:
            self.readonly = kwargs['readonly']
            del kwargs['readonly']
        else:
            self.readonly = False

        super(IggybasePasswordField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        return super(IggybasePasswordField, self).__call__(*args, **kwargs)


