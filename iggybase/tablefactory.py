from iggybase.admin.models import DataType, TableObject, Field
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, UniqueConstraint, or_
import sqlalchemy
from iggybase.database import db_session, Base
from types import new_class
from iggybase import utilities as util
import logging

class TableFactory:
    predefined_columns = ['id','name','description','date_created','last_modified','active','organization_id','order']

    def __init__(self, active=1):
        self.active = active
        self.session = db_session()

    def table_object_factory(self, class_name, table_object):
        classattr = {'table_type': 'user'}

        table_object_cols = self.fields(table_object.id)

        if not table_object_cols:
            return None

        # logging.info( 'table name: ' + class_name )
        for col in table_object_cols:
            if col.display_name in self.predefined_columns:
                continue

            # logging.info( col.field_name )
            if col.foreign_key_table_object_id is not None:
                foreign_table =  self.session.query(TableObject).filter_by(id=col.foreign_key_table_object_id).first()
                foreign_column = self.session.query(Field).filter_by(id=col.foreign_key_field_id).first()

                if foreign_table is not None and foreign_column is not None:
                    classattr[col.display_name] = self.create_column(col, foreign_table.name,
                                                                     foreign_column.display_name)

                    classattr[table_object.name + "_" + col.display_name + "_" + foreign_table.name] = \
                        self.create_foreign_key(TableFactory.to_camel_case(foreign_table.name), \
                                                classattr[col.display_name])
                else:
                    classattr[col.display_name] = self.create_column(col)
            else:
                classattr[col.display_name] = self.create_column(col)

        if table_object.extends_table_object_id is not None:
            logging.info('table_object.extends_table_object_id: ' + str(table_object.extends_table_object_id))
            logging.info('table_object.extends_table_object.name: ' + str(table_object.extends_table_object.name))
            table_base = __import__('iggybase.models.' +
                                           self.to_camel_case(table_object.extends_table_object.name))

            classattr = {'__mapper_args__': {'polymorphic_identity': table_object.name,}}
        else:
            table_base = Base

        newclass = new_class(class_name, (table_base,), {}, lambda ns: ns.update(classattr))

        return newclass

    @staticmethod
    def to_camel_case(snake_str):
        components = snake_str.split('_')

        return "".join(x.title() for x in components)

    def create_column(self, attributes, foreign_table_name=None, foreign_column_name=None):
        # logging.info('attributes.data_type_id: ' +str(attributes.data_type_id))
        datatype = self.session.query(DataType).filter_by(id=attributes.data_type_id).filter_by(active=1).first()

        if attributes.data_type_id == 6:
            # file datatype
            dtcname = getattr(sqlalchemy, 'String')
            dtinst = dtcname(250)
        elif attributes.data_type_id == 8 or attributes.data_type_id == 9:
            dtcname = getattr(sqlalchemy, 'Numeric')
            dtinst = dtcname(10, 2)
        elif attributes.data_type_id == 7:
            dtcname = getattr(sqlalchemy, 'Integer')
            dtinst = dtcname(11)
            foreign_table_name = 'long_text'
            foreign_column_name = 'long_text'
        else:
            dtcname = getattr(sqlalchemy, datatype.name)
            if attributes.data_type_id == 2:
                #string datatype
                dtinst = dtcname(attributes.length)
            else:
                dtinst = dtcname()

        arg = {}

        if attributes.primary_key == 1:
            arg['primary_key'] = True

        if attributes.unique == 1:
            arg['unique'] = True

        if attributes.default != "":
            arg['default'] = attributes.default

        if foreign_table_name is not None and foreign_column_name is not None:
            col = Column(dtinst, ForeignKey(foreign_table_name + "." + foreign_column_name), **arg)
        else:
            col = Column(dtinst, **arg)

        return col

    def create_foreign_key(self, foreign_table_name, foreign_column):

        arg = {}

        arg['foreign_keys'] = [foreign_column]

        return relationship(foreign_table_name, **arg)

    def table_objects(self, active=1):
        table_objects = []

        res = (self.session.query(TableObject).
               filter(TableObject.active==active).
               filter(or_(TableObject.admin_table==0, TableObject.admin_table is None)).
               order_by(TableObject.order))

        # query = res.statement.compile(dialect=mysql.dialect())
        # logging.info('query')
        # logging.info(str(query))
        # logging.info(str(query.params))

        res = res.all()

        for row in res:
            table_objects.append(row)
        return table_objects

    def fields(self, table_object_id):
        fields = []

        res = self.session.query(Field). \
            filter_by(table_object_id=table_object_id, active=self.active).all()

        for row in res:
            fields.append(row)

        return fields
