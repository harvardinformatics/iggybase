from iggybase.mod_admin.models import DataType, TableObject, Field
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, UniqueConstraint
import sqlalchemy
from iggybase.database import db_session, Base
from types import new_class
import datetime
import logging, sys, inspect


class TableFactory:
    def __init__(self, active=1):
        self.active = active

    def table_object_factory(self, class_name, table_object):
        classattr = {"__tablename__": table_object.name}

        table_object_cols = self.fields(table_object.id, self.active)

        if not table_object_cols:
            return None

        logging.info( 'table name: ' + class_name )
        for col in table_object_cols:
            logging.info( col.field_name )
            if col.foreign_key_table_object_id is not None:
                foreign_table = db_session.query(TableObject).filter_by(id=col.foreign_key_table_object_id).first()
                foreign_column = db_session.query(Field).filter_by(id=col.foreign_key_field_id).first()

                classattr[col.field_name] = self.create_column(col, foreign_table.name, foreign_column.field_name)

                if foreign_table is not None and foreign_column is not None:
                    classattr[table_object.name + "_" + col.field_name + "_" + foreign_table.name] = \
                        self.create_foreign_key(TableFactory.to_camel_case(foreign_table.name), \
                                                classattr[col.field_name])
            else:
                classattr[col.field_name] = self.create_column(col)

        classattr['__table_args__'] = {'mysql_engine': 'InnoDB'}

        newclass = new_class(class_name, (Base,), {}, lambda ns: ns.update(classattr))

        return newclass

    @staticmethod
    def to_camel_case(snake_str):
        components = snake_str.split('_')

        return "".join(x.title() for x in components)

    def create_column(self, attributes, foreign_table_name=None, foreign_column_name=None):
        datatype = db_session.query(DataType).filter_by(id=attributes.data_type_id).filter_by(active=1).first()

        dtcname = getattr(sqlalchemy, datatype.name)
        if attributes.data_type_id == 2:
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
            return Column(dtinst, ForeignKey(foreign_table_name + "." + foreign_column_name), **arg)
        else:
            return Column(dtinst, **arg)

    def create_foreign_key(self, foreign_table_name, foreign_column):

        arg = {}

        arg['foreign_keys'] = [foreign_column]

        return relationship(foreign_table_name, **arg)

    def table_objects(self, active=1):
        table_objects = []

        res = db_session.query(TableObject).filter_by(admin_table_object!=1).filter_by(active=active). \
            order_by(TableObject.order).all()

        for row in res:
            table_objects.append(row)

        return table_objects

    def fields(self, table_object_id, active=1):
        fields = []

        res = db_session.query(Field). \
            filter_by(table_object_id=table_object_id, active=active).all()

        for row in res:
            fields.append(row)

        return fields
