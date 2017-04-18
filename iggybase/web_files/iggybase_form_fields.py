from wtforms import StringField, IntegerField, BooleanField, DateField, TextAreaField, FloatField, SelectField,\
    FileField, PasswordField, DecimalField, DateTimeField


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

        self.readonly = kwargs['readonly']
        del kwargs['readonly']

        if self.readonly:
            self.iggybase_class = temp_class

        self.table_object = kwargs['table_object']
        del kwargs['table_object']

        self.instance_name = kwargs['instance_name']
        del kwargs['instance_name']

        super(IggybaseLookUpField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.readonly:
            kwargs.setdefault('readonly', True)
        else:
            kwargs.setdefault('data-toggle', "modal")

        kwargs['data-table-object'] = self.table_object
        kwargs['data-instance-name'] = self.instance_name

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

        self.table_object = kwargs['table_object']
        del kwargs['table_object']

        self.instance_name = kwargs['instance_name']
        del kwargs['instance_name']

        super(IggybaseSelectField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        kwargs['data-table-object'] = self.table_object
        kwargs['data-instance-name'] = self.instance_name

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

        self.table_object = kwargs['table_object']
        del kwargs['table_object']

        self.instance_name = kwargs['instance_name']
        del kwargs['instance_name']

        super(IggybaseBooleanField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        kwargs['data-table-object'] = self.table_object
        kwargs['data-instance-name'] = self.instance_name

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

        self.readonly = kwargs['readonly']
        del kwargs['readonly']

        if self.readonly:
            # remove datepicker for readonly
            self.iggybase_class = temp_class

        self.iggybase_class += ' date-field'

        self.table_object = kwargs['table_object']
        del kwargs['table_object']

        self.instance_name = kwargs['instance_name']
        del kwargs['instance_name']

        super(IggybaseDateField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        kwargs['data-table-object'] = self.table_object
        kwargs['data-instance-name'] = self.instance_name

        return super(IggybaseDateField, self).__call__(*args, **kwargs)


class IggybaseDateTimeField(DateTimeField):
    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
            del kwargs['title']
        else:
            self.title = None

        if 'iggybase_class' in kwargs:
            self.iggybase_class = 'datetimepicker ' + kwargs['iggybase_class']
            temp_class = kwargs['iggybase_class']
            del kwargs['iggybase_class']
        else:
            self.iggybase_class = 'datetimepicker'

        self.readonly = kwargs['readonly']
        del kwargs['readonly']

        if self.readonly:
            # remove datepicker for readonly
            self.iggybase_class = temp_class

        self.iggybase_class += ' datetime-field'

        self.table_object = kwargs['table_object']
        del kwargs['table_object']

        self.instance_name = kwargs['instance_name']
        del kwargs['instance_name']

        super(IggybaseDateTimeField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        kwargs['data-format'] = 'yyyy-MM-dd hh:mm:ss'
        kwargs['data-table-object'] = self.table_object
        kwargs['data-instance-name'] = self.instance_name

        return super(IggybaseDateTimeField, self).__call__(*args, **kwargs)


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

        self.table_object = kwargs['table_object']
        del kwargs['table_object']

        self.instance_name = kwargs['instance_name']
        del kwargs['instance_name']

        super(IggybaseTextAreaField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        kwargs['data-table-object'] = self.table_object
        kwargs['data-instance-name'] = self.instance_name

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

        self.table_object = kwargs['table_object']
        del kwargs['table_object']

        self.instance_name = kwargs['instance_name']
        del kwargs['instance_name']

        super(IggybaseFloatField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        kwargs['data-table-object'] = self.table_object
        kwargs['data-instance-name'] = self.instance_name

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

        self.table_object = kwargs['table_object']
        del kwargs['table_object']

        self.instance_name = kwargs['instance_name']
        del kwargs['instance_name']

        super(IggybaseDecimalField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        kwargs['data-table-object'] = self.table_object
        kwargs['data-instance-name'] = self.instance_name

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

        self.table_object = kwargs['table_object']
        del kwargs['table_object']

        self.instance_name = kwargs['instance_name']
        del kwargs['instance_name']

        super(IggybaseIntegerField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        kwargs['data-table-object'] = self.table_object
        kwargs['data-instance-name'] = self.instance_name

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

        self.table_object = kwargs['table_object']
        del kwargs['table_object']

        self.instance_name = kwargs['instance_name']
        del kwargs['instance_name']

        super(IggybaseStringField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        kwargs['data-table-object'] = self.table_object
        kwargs['data-instance-name'] = self.instance_name

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

        self.table_object = kwargs['table_object']
        del kwargs['table_object']

        self.instance_name = kwargs['instance_name']
        del kwargs['instance_name']

        super(IggybaseFileField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        kwargs.setdefault('multiple', True)

        kwargs['data-table-object'] = self.table_object
        kwargs['data-instance-name'] = self.instance_name

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

        self.table_object = kwargs['table_object']
        del kwargs['table_object']

        self.instance_name = kwargs['instance_name']
        del kwargs['instance_name']

        super(IggybasePasswordField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.title is not None:
            kwargs['title'] = self.title

        if self.iggybase_class is not None:
            kwargs['class'] = self.iggybase_class

        if self.readonly:
            kwargs.setdefault('readonly', True)

        kwargs['data-table-object'] = self.table_object
        kwargs['data-instance-name'] = self.instance_name

        return super(IggybasePasswordField, self).__call__(*args, **kwargs)
