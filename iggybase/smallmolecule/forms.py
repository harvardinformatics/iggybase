from flask_wtf import Form
from wtforms import (IntegerField, FloatField, FileField, StringField,
    TextAreaField)
from wtforms.validators import Regexp

class LipidAnalysisForm(Form):
    cols_to_remove = ['ARatio', 'HRatio', 'ADiff', 'HDiff', 'GroupHeight', 'HeightRSD',
    'Height', 'NormArea', 'NormHeight', 'Hwhm(L)', 'Hwhm(R)', 'AreaScore', 'DataId', 'Scan',
    'It.', 'z', 'Delta(Da)', 'mScore', 'Occupy']

    file_msg = 'Must submit a file to process'
    file_regex = "[\w]*"
    retention_time_filter = IntegerField('Retention Time', default = 3)
    group_pq_filter = FloatField('GroupPQ', default = 0.8)
    group_sn_filter = IntegerField('GroupS/N', default = 100)
    group_area_filter = IntegerField('Group Area', default = 0)
    group_height_filter = IntegerField('Group Height', default = 0)
    file1 = FileField('File 1', [Regexp(file_regex, message = file_msg)])
    file2 = FileField('File 2')
    blank = StringField('Normalize using blank')
    mult_factor = IntegerField('Blank Multiplication Factor', default = 3)
    remove_cols = TextAreaField('Columns to remove (comma seperated)', default =
            ', '.join(cols_to_remove))




