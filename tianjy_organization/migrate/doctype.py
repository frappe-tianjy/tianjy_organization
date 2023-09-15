from typing import Any
import frappe
from frappe.model.meta import Meta
from frappe.query_builder import DocType
from frappe.query_builder.functions import Max, Coalesce


def _field_where(dt: str, df: str = ''):
	Table = DocType('DocField')
	where = (Table.parent == dt)
	where = where & (Table.parenttype == 'DocType')
	where = where & (Table.parentfield == 'fields')
	if df: where = where & (Table.fieldname == df)

	return where


def get_idx(dt: str, next: str | None = None) -> int:
	Table = DocType('DocField')
	if next:
		idx_list: list[int] = (frappe.qb.from_(Table)
			.select('idx')
			.where(_field_where(dt, next))
			.limit(1)
		).run(pluck=True)
		if idx_list: return idx_list[0]
	idx_list: list[int] = (frappe.qb.from_(Table)
		.select(Coalesce(Max(Table.idx), 0))
		.where(_field_where(dt))
	).run(pluck=True)
	if idx_list:
		return idx_list[0] + 1
	return 1




def add_filed(dt: str, field, next: str | None = None):
	"""追加字段"""
	fieldname = field['fieldname']
	Table = DocType('DocField')
	values: list[str] = (frappe.qb.from_(Table)
		.select('options')
		.where(_field_where(dt, fieldname))
		.limit(1)
	).run(pluck=True)
	if values:
		return False

	idx: int = get_idx(dt, next)

	q = frappe.qb.update(Table)
	q = q.set(Table.idx, Table.idx + 1)
	q = q.where(_field_where(dt) & (Table.idx >= idx))
	print(str(q))
	q.run()

	q = frappe.qb.into(Table)
	q = q.columns(
		'name', 'parent', 'parenttype', 'parentfield', 'idx',
		'default', 'fieldname', 'fieldtype', 'label', 'options', "collapsible",
	).insert(
		frappe.generate_hash(), dt, 'DocType', 'fields', idx,
		field.get('default', None),
		fieldname,
		field['fieldtype'],
		field.get('label', None),
		field.get('options', None),
		field.get('collapsible', 0),
	)
	print(str(q))
	q.run()
	return True


def update_doctype_db(dt):
	self = frappe.get_doc('DocType', dt)
	frappe.db.updatedb(self.name, Meta(self))


def update_doctype(dt: str, values: dict[str, Any]):
	Table = DocType('DocType')
	q = frappe.qb.update(Table)
	for k, v in values.items():
		q = q.set(Table[k], v)
	q = q.where(Table.name == dt)
	print(str(q))
	q.run()


def run():
	add_filed('DocType', {
		'fieldname': 'tianjy_organization_filter_method',
		"fieldtype": "Select",
		"label": "视图默认过滤方式",
		"options": "Equal\nDescendants",
		"default": "Equal",
	}, 'view_settings')
	add_filed('DocType', {
		'fieldname': 'column_break_tianjy_organization',
		"fieldtype": "Column Break",
	}, 'tianjy_organization_filter_method')
	add_filed('DocType', {
		'fieldname': 'tianjy_organization_field',
		"fieldtype": "Data",
		"label": "Field",
		"options": "",
	}, 'column_break_tianjy_organization')
	add_filed('DocType', {
		"collapsible": 1,
		'fieldname': 'section_break_tianjy_organization',
		"fieldtype": "Section Break",
		"label": "组织关联方式",
	}, 'tianjy_organization_field')

	update_doctype_db('DocType')
