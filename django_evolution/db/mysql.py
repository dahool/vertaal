from django.core.management import color

from common import BaseEvolutionOperations

class EvolutionOperations(BaseEvolutionOperations):
    def rename_column(self, opts, old_field, f):
        if old_field.column == f.column:
            # No Operation
            return []

        qn = self.connection.ops.quote_name
        style = color.no_style()

        ###
        col_type = f.db_type(connection=self.connection)
        tablespace = f.db_tablespace or opts.db_tablespace
        if col_type is None:
            # Skip ManyToManyFields, because they're not represented as
            # database columns in this table.
            return []
        # Make the definition (e.g. 'foo VARCHAR(30)') for this field.
        field_output = [style.SQL_FIELD(qn(f.column)),
            style.SQL_COLTYPE(col_type)]
        field_output.append(style.SQL_KEYWORD('%sNULL' % (not f.null and 'NOT ' or '')))
        if f.primary_key:
            field_output.append(style.SQL_KEYWORD('PRIMARY KEY'))
        if f.unique:
            field_output.append(style.SQL_KEYWORD('UNIQUE'))
        if tablespace and self.connection.features.supports_tablespaces and (f.unique or f.primary_key) and self.connection.features.autoindexes_primary_keys:
            # We must specify the index tablespace inline, because we
            # won't be generating a CREATE INDEX statement for this field.
            field_output.append(self.connection.ops.tablespace_sql(tablespace, inline=True))
        if f.rel:
            field_output.append(style.SQL_KEYWORD('REFERENCES') + ' ' + \
                style.SQL_TABLE(qn(f.rel.to._meta.db_table)) + ' (' + \
                style.SQL_FIELD(qn(f.rel.to._meta.get_field(f.rel.field_name).column)) + ')' +
                self.connection.ops.deferrable_sql()
            )

        params = (qn(opts.db_table), qn(old_field.column), ' '.join(field_output))
        return ['ALTER TABLE %s CHANGE COLUMN %s %s;' % params]

    def set_field_null(self, model, f, null):
        qn = self.connection.ops.quote_name
        params = (qn(model._meta.db_table), qn(f.column),
                  f.db_type(connection=self.connection))
        if null:
            return 'ALTER TABLE %s MODIFY COLUMN %s %s DEFAULT NULL;' % params
        else:
            return 'ALTER TABLE %s MODIFY COLUMN %s %s NOT NULL;' % params

    def change_max_length(self, model, field_name, new_max_length, initial=None):
        qn = self.connection.ops.quote_name
        opts = model._meta
        f = opts.get_field(field_name)
        f.max_length = new_max_length
        params = {
            'table': qn(opts.db_table),
            'column': qn(f.column),
            'length': f.max_length,
            'type': f.db_type(connection=self.connection)
        }
        return ['UPDATE %(table)s SET %(column)s=LEFT(%(column)s,%(length)d);' % params,
                'ALTER TABLE %(table)s MODIFY COLUMN %(column)s %(type)s;' % params]

    def drop_index(self, model, f):
        qn = self.connection.ops.quote_name
        params = (qn(self.get_index_name(model, f)), qn(model._meta.db_table))
        return ['DROP INDEX %s ON %s;' % params]

    def change_unique(self, model, field_name, new_unique_value, initial=None):
        qn = self.connection.ops.quote_name
        opts = model._meta
        f = opts.get_field(field_name)
        constraint_name = '%s' % (f.column,)
        if new_unique_value:
            params = (constraint_name, qn(opts.db_table), qn(f.column),)
            return ['CREATE UNIQUE INDEX %s ON %s(%s);' % params]
        else:
            params = (constraint_name, qn(opts.db_table))
            return ['DROP INDEX %s ON %s;' % params]

    def rename_table(self, model, old_db_tablename, db_tablename):
        if old_db_tablename == db_tablename:
            return []

        qn = self.connection.ops.quote_name
        params = (qn(old_db_tablename), qn(db_tablename))
        return ['RENAME TABLE %s TO %s;' % params]

    def change_type(self, model, field, initial=None):
        qn = self.connection.ops.quote_name
    
        if field.rel:
            # it is a foreign key field
            related_model = field.rel.to
            related_table = related_model._meta.db_table
            related_pk_col = related_model._meta.pk.name
            constraints = ['%sNULL' % (not field.null and 'NOT ' or '')]
            if field.unique or field.primary_key:
                constraints.append('UNIQUE')
            params = (qn(model._meta.db_table), qn(field.column), field.db_type(), ' '.join(constraints), 
                qn(related_table), qn(related_pk_col), connection.ops.deferrable_sql())
            output = ['ALTER TABLE %s MODIFY %s %s %s REFERENCES %s (%s) %s;' % params]
        else:
            null_constraints = '%sNULL' % (not field.null and 'NOT ' or '')
            if field.unique or field.primary_key:
                unique_constraints = 'UNIQUE'
            else:
                unique_constraints = ''
            params = (qn(model._meta.db_table), qn(field.column), field.db_type(),' '.join([null_constraints, unique_constraints]))
            output = ['ALTER TABLE %s MODIFY %s %s %s;' % params]
        return output        