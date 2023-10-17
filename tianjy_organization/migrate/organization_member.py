from frappe.query_builder import DocType
import frappe


def run():
    Table = DocType('Tianjy Organization Member')
    q = frappe.qb.update(Table).where(Table.is_inherit.isnull())
    q = q.set(Table['is_inherit'], 0)
    q = q.set(Table['inherit_from'], Table.organization)
    q.run()
