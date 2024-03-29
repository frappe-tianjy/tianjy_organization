# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
"""build query for doclistview and return results"""


from typing import Any
import frappe
import frappe.defaults
import frappe.permissions
import frappe.model.db_query
from frappe.model.db_query import cast_name
from frappe.query_builder.utils import DocType
import frappe.share
from frappe import _
from frappe.utils import (
	get_filter,
	cstr,
)
from ..tianjy_organization.doctype.tianjy_organization.tianjy_organization import TianjyOrganization
from ..filter import filter_operators

old_prepare_filter_condition = frappe.model.db_query.DatabaseQuery.prepare_filter_condition

def prepare_filter_condition(self: frappe.model.db_query.DatabaseQuery, f):
	"""Returns a filter condition in the format:
	ifnull(`tabDocType`.`fieldname`, fallback) operator "value"
	"""

	from frappe.boot import get_additional_filters_from_hooks

	additional_filters_config = get_additional_filters_from_hooks()
	filter = get_filter(self.doctype, f, additional_filters_config)

	operator = filter.operator.lower()
	doctype = filter.doctype
	value = filter.value
	fieldname = filter.fieldname
	if operator not in filter_operators:
		return old_prepare_filter_condition(self, f)

	field = frappe.get_meta(doctype).get_field(fieldname)
	ref_doctype = field.options if field else doctype
	if not ref_doctype: return old_prepare_filter_condition(self, f)

	tname = "`tab" + doctype + "`"
	if tname not in self.tables:
		self.append_table(tname)

	if 'organizations' in operator and isinstance(value, str):
		value = [v for v in set(value.split(',')) if v]
	if value == '~':
		organization = frappe.get_request_header('X-Tianjy-Organization', "")
		value = organization if isinstance(organization, str) else ''
	elif isinstance(value, list) and '~' in value:
		value = [v for v in value if value != '~']
		organization = frappe.get_request_header('X-Tianjy-Organization', "")
		if organization and isinstance(organization, str): value.append(organization)

	if 'module' in operator:
		# 查询开启模块的组织
		value = value.split(',') if isinstance(value, str) else value
		value = [v for v in set(value) if v] if isinstance(value, (list, set, tuple)) else value
		if value and isinstance(value, list):
			Table = DocType('Tianjy Organization Enabled Module')
			q = frappe.qb.from_(Table)
			q = q.select(Table.parent)
			q = q.where(
				(Table.parentfield == 'modules') &
				(Table.parenttype == TianjyOrganization.DOCTYPE) &
				Table.module.isin(value)
			)
			value = q.run(pluck=True)
			disabled = 'disabled' in operator
			ancestors = 'ancestors' in operator
			descendants = 'descendants' in operator
			operator = 'organizations'
			if ancestors:
				operator = 'organization ancestors'
			if descendants:
				operator = 'organization descendants'
			if disabled:
				operator = f'not {operator}'
		else:
			value = ''
	if not value: return '0 = 0'

	filters: dict[str, Any] | None = None
	if operator in ('organization', 'organizations', 'not organization', 'not organizations'):
		filters=dict(name=('in', value) if isinstance(value, list) else value)
	elif value := frappe.db.get_value(TianjyOrganization.DOCTYPE, value, ["lft", "rgt"]):
		lft, rgt = value
		lft_o, rgt_o = [">=", "<="] if 'descendants' in operator else["<=", ">="];
		filters=dict(lft=[lft_o, lft], rgt=[rgt_o, rgt])

	documents = []
	if filters:
		pluck='name'
		if ref_doctype != TianjyOrganization.DOCTYPE:
			filters['doc_type'] = ref_doctype
			filters['document'] = ('is', 'set')
			pluck='document'
		documents = frappe.get_all(TianjyOrganization.DOCTYPE, filters=filters, pluck=pluck)

	is_not = 'not ' in operator
	if not documents: return '0 = 0' if is_not else '1 = 0'
	value = [frappe.db.escape((cstr(v) or "").strip(), percent=False) for v in documents]
	value = f"({', '.join(value)})"

	operator = "not in" if is_not else "in"

	column_name = cast_name(fieldname if "ifnull(" in fieldname else f"{tname}.`{fieldname}`")

	if (self.ignore_ifnull or "ifnull(" in column_name.lower()):
		condition = f"{column_name} {operator} {value}"
	else:
		fallback = "''"
		condition = f"ifnull({column_name}, {fallback}) {operator} {value}"

	return condition





frappe.model.db_query.DatabaseQuery.prepare_filter_condition = prepare_filter_condition
