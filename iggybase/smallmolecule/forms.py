from flask_wtf import Form
from wtforms import (IntegerField, FloatField, StringField,
    TextAreaField, RadioField)
from wtforms.validators import Optional
from flask_wtf.file import FileField, FileRequired


class ElseOptional(Optional):
    def __init__(self, attr, val, *args, **kwargs):
        self.attr = attr
        self.val = val
        super(ElseOptional, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        if getattr(form, self.attr).data != self.val:
            super(ElseOptional, self).__call__(form, field)

class LipidAnalysisForm(Form):
    cols_to_remove = ['ARatio', 'HRatio', 'ADiff', 'HDiff', 'GroupHeight', 'HeightRSD',
    'Height', 'NormArea', 'NormHeight', 'Hwhm(L)', 'Hwhm(R)', 'AreaScore', 'DataId', 'Scan',
    'It.', 'z', 'Delta(Da)', 'mScore', 'Occupy']

    file_msg = 'Must submit a file to process'
    retention_time_filter = IntegerField('Retention Time', default = 3)
    group_pq_filter = FloatField('GroupPQ', default = 0.8)
    group_sn_filter = IntegerField('GroupS/N', default = 100)
    group_area_filter = IntegerField('Group Area', default = 0)
    group_height_filter = IntegerField('Group Height', default = 0)
    file1 = FileField('File 1', [FileRequired()])
    file2 = FileField('File 2')
    blank = StringField('Name of the blank (exp. c, s1, s2)')
    mult_factor = IntegerField('Blank Multiplication Factor', default = 3)
    remove_cols = TextAreaField('Columns to remove (comma seperated)', default =
            ', '.join(cols_to_remove))
    normalize = RadioField('Normalization', choices = [('none', 'None'),
    ('intensity', 'Sum of area intensities'), ('values', 'Enter values')], default = 'none')
    normal_c = StringField('c')
    normal_s1 = StringField('s1')
    normal_s2 = StringField('s2')
    normal_s3 = StringField('s3')
    normal_s4 = StringField('s4')
    normal_s5 = StringField('s5')
    normal_s6 = StringField('s6')
    normal_s7 = StringField('s7')
    normal_s8 = StringField('s8')
    normal_s9 = StringField('s9')
    normal_s10 = StringField('s10')





