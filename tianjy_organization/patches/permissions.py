import frappe.permissions
import frappe.model.db_query

old_has_controller_permissions = frappe.permissions.has_controller_permissions

def has_controller_permissions(doc, ptype, user=None):
	from .. import has_permission
	if has_permission(doc, ptype, user or frappe.session.user) == False: # type: ignore
		return False

	return old_has_controller_permissions(doc, ptype, user)

frappe.permissions.has_controller_permissions = has_controller_permissions


old_get_permission_query_conditions = frappe.model.db_query.DatabaseQuery.get_permission_query_conditions

def get_permission_query_conditions(self) -> str:
	from .. import get_permission_query_conditions
	condition = get_permission_query_conditions(self.doctype, self.user) or ''
	if condition == '1 = 0':
		return condition

	old_condition = old_get_permission_query_conditions(self)

	if condition and old_condition:
		return " and ".join([condition, old_condition])
	return condition or old_condition

frappe.model.db_query.DatabaseQuery.get_permission_query_conditions = get_permission_query_conditions # type: ignore
