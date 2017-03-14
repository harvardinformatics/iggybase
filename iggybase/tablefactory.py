from iggybase.admin.models import DataType, TableObject, Field
from sqlalchemy.orm import relationship, aliased
from sqlalchemy import Column, ForeignKey, UniqueConstraint, or_
import sqlalchemy
from iggybase.database import db_session, Base
from types import new_class
import logging

class TableFactory:
    predefined_columns = ['id','name','description','date_created','last_modified','active','organization_id','order']

    def __init__(self, active=1):
        self.active = active
        self.session = db_session()

    def table_object_factory(self, class_name, table_object, extend_class = None, extend_table = None,
                             is_extended = None):
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
                elif col.select_list_id is not None:
                    classattr[col.display_name] = self.create_column(col, 'select_list_item','name')

                    classattr[table_object.name + "_" + col.display_name + "_select_list_item"] = \
                        self.create_foreign_key('SelectListItem', classattr[col.display_name])
                else:
                    classattr[col.display_name] = self.create_column(col)
            else:
                classattr[col.display_name] = self.create_column(col)

        if extend_class is not None:
            # this will always join on id
            id_col = lambda: None
            id_col.data_type_id = 1
            id_col.select_list_id = None
            id_col.primary_key = 1
            id_col.default = ''
            id_col.unique = 0

            classattr['id'] = self.create_column(id_col, extend_table, 'id')

            classattr[table_object.name + "_id_" + extend_table] = \
                self.create_foreign_key(TableFactory.to_camel_case(extend_table), classattr['id'])

            table_base = extend_class

            classattr['__mapper_args__'] = {'polymorphic_identity': table_object.name,}
        else:
            table_base = Base
            if is_extended:
                classattr['__mapper_args__'] = {'polymorphic_identity': table_object.name,'polymorphic_on':
                    classattr['type']}

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
        arg = {'foreign_keys': foreign_column}

        return relationship(foreign_table_name, **arg)

    def table_objects(self, active=1):
        table_objects = []

        Extension = aliased(TableObject, name='Extension')
        Extended = aliased(TableObject, name='Extended')

        res = (self.session.query(TableObject, Extension, Extended).
               outerjoin(Extension, TableObject.extends_table_object_id == Extension.id).
               outerjoin(Extended, TableObject.id == Extended.extends_table_object_id).
               filter(TableObject.active==active).
               filter(or_(TableObject.admin_table==0, TableObject.admin_table is None)).
               order_by(TableObject.order)).all()

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
