class IggybaseFormObject():
    def __init__(self, props):
        if props is None:
            props= {}

        self.props = props

    def props_to_string(self):
        prop_string = ''

        for key, value in self.props.items():
            prop_string += key +"='" + value + "' "

        return prop_string


class IggybaseFormContainer(IggybaseFormObject):
    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, index):
        return self.children[index]

    def keys(self):
        return range(len(self.children))

    def items(self):
        return enumerate(self.children)

    def values(self):
        return self.children

    def __init__(self, props=None):
        self.children = []
        super(IggybaseFormContainer, self).__init__(props)

    def add_child(self, child_record):
        self.children.append(child_record)

        return len(self.children) - 1


class IggybaseFormTable(IggybaseFormContainer):
    def __init__(self, table_name, title='Data', level=0, display='vertical', table_class=None, props=None):
        self.table_name = table_name
        self.level = level
        self.title = title
        self.display = display
        self.top_buttons = []
        self.bottom_buttons = []
        self.field_display_names = []

        if table_class is None:
            self.table_class = " div_level_" + str(level)
        else:
            self.table_class = table_class + " div_level_" + str(level)

        super(IggybaseFormTable, self).__init__(props)

    def add_new_record(self, record_name, new_record=False, row_class=None, row_props=None):
        child_record = IggybaseFormRecord(new_record, row_class, row_props)
        self.add_child(child_record)

        return len(self.children) - 1

    def add_record(self, record):
        self.add_child(record)

        return len(self.children) - 1

    def add_buttons(self, top_buttons, bottom_buttons):
        for button in top_buttons:
            self.top_buttons.append(IggybaseFormButton(button))

        for button in bottom_buttons:
            self.bottom_buttons.append(IggybaseFormButton(button))


class IggybaseFormRecord(IggybaseFormContainer):
    def __init__(self, record_name, new_record=False, row_class=None, props=None):
        self.row_class = row_class
        self.new_record = new_record
        self.record_name = record_name

        super(IggybaseFormRecord, self).__init__(props)

    def add_new_field(self, field_id, field_class, field_props=None):
        child_record = IggybaseFormField(field_id, field_class, field_props)
        self.add_child(child_record)

        return len(self.children) - 1

    def add_field(self, field):
        self.add_child(field)

        return len(self.children) - 1


class IggybaseFormField(IggybaseFormObject):
    def __init__(self, field_id, field_class, props=None):
        self.field_id = field_id
        self.field_class = field_class

        if field_class is not None:
            self.wide = "wide" in field_class

        super(IggybaseFormField, self).__init__(props)


class IggybaseFormButton(IggybaseFormObject):
    def __init__(self, props=None):
        self.special_props = props.pop('special_props', '')

        super(IggybaseFormButton, self).__init__(props)

