import frappe
from frappe.exceptions import DoesNotExistError

from .tianjy_organization.doctype.tianjy_organization_workspace.tianjy_organization_workspace import TianjyOrganizationWorkspace
from . import get_user_organizations, user_organizations_sql, to_permission_type


def get_organization_permission_query_conditions(user=None) -> str:
	"""
	获取用户在某组织内的角色，如果用户在组织内相关权限时，则返回 None 而非数组
	"""
	if user == 'Administrator': return ''
	if 'Tianjy Organization Manager' in frappe.get_roles(user): return ''
	return f"`tabTianjy Organization`.`name` in ({user_organizations_sql(user)})"

def has_permission(doc, ptype, user):
	if to_permission_type(ptype) != 'viewable': return
	if user == 'Administrator': return
	if 'Tianjy Organization Manager' in frappe.get_roles(user): return
	if doc.name in get_user_organizations(user): return
	return False


@frappe.whitelist()
def get_default_workspace(organization: str = ''):
	if not organization:
		return
	try:
		doc: TianjyOrganizationWorkspace = frappe.get_last_doc(TianjyOrganizationWorkspace.DOCTYPE, dict(
			organization=organization,
			default=1
		)) # type: ignore
		return doc.workspace # type: ignore
	except DoesNotExistError:
		...
