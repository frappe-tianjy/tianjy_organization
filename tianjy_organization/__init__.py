
__version__ = '0.0.1'

from typing import Literal

import frappe
import frappe.permissions
from frappe.model.document import Document
from frappe.utils import cint
from frappe.query_builder.utils import DocType

from .tianjy_organization.doctype.tianjy_organization.tianjy_organization import TianjyOrganization
from .tianjy_organization.doctype.tianjy_organization_member.tianjy_organization_member import TianjyOrganizationMember
from .tianjy_organization.doctype.tianjy_organization_role.tianjy_organization_role import TianjyOrganizationRole


def _get_user(user: str | None = None) -> str:
	return user or frappe.session.user # type: ignore

member_type = Literal['visible', 'viewable', 'updatable', 'addible', 'editable', 'deletable', 'manageable']
viewable_type = Literal['viewable', 'updatable', 'addible', 'editable', 'deletable']

def member_type_sql_where(type: member_type) -> str:
	if type == 'updatable':
		return '(addible = 1 OR editable = 1)'
	if type in ['viewable', 'addible', 'editable', 'deletable', 'manageable']:
		return f'{type} = 1'
	return 'visible = 1'

def member_type_qb_where(type: member_type) -> str:
	Table = DocType(TianjyOrganizationMember.DOCTYPE)
	if type == 'updatable':
		return (Table.addible == 1) | (Table.editable == 1)
	if type in ['viewable', 'addible', 'editable', 'deletable', 'manageable']:
		return Table[type] == 1
	return Table.visible == 1

def organization_members_sql(organization: str, type: member_type = 'visible') -> str:
	"""获取在指定组织内有指定类型的用户的SQL语句"""
	sql = f'SELECT DISTINCT user FROM `tab{TianjyOrganizationMember.DOCTYPE}`'
	sql = f'{sql} WHERE organization={frappe.db.escape(organization, percent=False)} AND {member_type_sql_where(type)}'
	return sql

def user_organizations_sql(user = None, type: member_type = 'visible') -> str:
	"""获取在指定用户有指定类型的组织的SQL语句"""
	sql = f'SELECT DISTINCT organization FROM `tab{TianjyOrganizationMember.DOCTYPE}`'
	sql = f'{sql} WHERE user={frappe.db.escape(_get_user(user), percent=False)} AND {member_type_sql_where(type)}'
	return sql



def get_user_organizations(user = None, type: member_type = 'visible') -> list[str]:
	"""获取用户在拥有特定权限的组织"""
	return [v[0] for v in frappe.db.sql(user_organizations_sql(user, type))]

def get_organization_members(organization:str, type: member_type = 'visible') -> list[str]:
	"""获取组织中拥有特定权限的用户"""
	return [v[0] for v in frappe.db.sql(organization_members_sql(organization, type))]



def get_roles(organization: str, user=None, type: viewable_type = 'viewable') -> list[str] | None:
	"""获取用户在某组织内的角色，如果用户在组织内无相关权限时，则返回 None 而非数组"""
	if not organization: return
	if not isinstance(organization, str): return

	members = frappe.get_all(
		TianjyOrganizationMember.DOCTYPE,
		filters = {
			"organization": organization,
			"user": _get_user(user),
			type if type in ['addible', 'editable', 'deletable'] else 'viewable': 1,
		},
		or_filters = dict(addible=1,editable=1) if type == 'updatable' else None,
		fields=['organization', 'inherit_from']
	);


	if not members: return

	organizations = [m['inherit_from'] or m['organization'] for m in members]

	return list(set(frappe.get_all(TianjyOrganizationRole.DOCTYPE, filters={
		'user': user,
		'organization': ('in', organizations),
	}, pluck="role")))


def get_user_organizations_by_role(
	role: str | list[str],
	user = None,
	type: member_type = 'viewable',
) -> list[str]:
	"""获取用户拥有特定角色的组织列表"""
	user = _get_user(user)
	organizations = frappe.get_all(TianjyOrganizationRole.DOCTYPE, filters={
		"user": user,
		"role": ('in', role) if isinstance(role, list) else role
	}, pluck="organization")
	if not organizations: return []
	Table = DocType(TianjyOrganizationMember.DOCTYPE)
	q = frappe.qb.from_(Table)
	q = q.select(Table.organization)
	q = q.where(
		(Table.user == user) & member_type_qb_where(type) & (
			(Table.inherit_from.isin(organizations)) |
			Table.organization.isin(organizations)
		)
	)
	return q.run(pluck=True)



def get_user_organizations_by_doctype_permission(
	doctype: str,
	user: str | None = None,
) -> list[str]:
	"""获取当前用户在特定 DocType 内有权限的组织列表"""
	doctype_roles = frappe.permissions.get_doctype_roles(doctype)
	return get_user_organizations_by_role(doctype_roles, user)

def get_permission_query_conditions(
	doctype: str,
	user: str | None = None,
	organization_field: str = 'organization'
):
	"""
	获取列表查询条件
	e.g.

	### Test Doctype 自定义的 get_permission_query_conditions 函数
	```python
	import tianjy_organization
	def get_permission_query_conditions(user):
		# 注意指明 doctype 参数为当前 doctype
		return tianjy_organization.get_permission_query_conditions('Test Doctype', user, 'organization')
	```
	### hooks.py 文件定义钩子

	```python
	permission_query_conditions = {
		## 使用上面自定义的钩子
		"Test Doctype": ".....get_permission_query_conditions",
	}
	```
	"""
	user = _get_user(user)
	if user == 'Administrator': return

	organizations = set(get_user_organizations_by_doctype_permission(doctype, user))
	if not organizations: return "1 = 0"

	values = ', '.join([frappe.db.escape(o, percent=False) for o in organizations])
	return f"`tab{doctype}`.`{organization_field}` in ({values})"

def get_visible_query_conditions(
	doctype: str,
	user: str | None = None,
	organization_field: str = 'organization'
):
	"""获取列表查询条件"""
	return f"`tab{doctype}`.`{organization_field}` in ({user_organizations_sql(user)})"




def _get_user_permissions_in_organization(meta, organization, user=None, is_owner=None, type: viewable_type = 'viewable'):
	"""
	Returns dict of evaluated role permissions like
	        {
	                "read": 1,
	                "write": 0,
	                // if "if_owner" is enabled
	                "if_owner":
	                        {
	                                "read": 1,
	                                "write": 0
	                        }
	        }
	"""
	user = _get_user(user)
	if user == "Administrator": return None

	if isinstance(meta, str): meta = frappe.get_meta(meta)


	cache_key = (meta.name, organization, user)

	# if perms := frappe.local.role_permissions.get(cache_key):
	# 	return perms


	roles = get_roles(organization, user, type)
	if not roles:
		perms = frappe._dict(if_owner={}, has_if_owner_enabled=False)
		for ptype in frappe.permissions.rights: perms[ptype] = 0
		# frappe.local.role_permissions[cache_key] = perms
		return perms

	def is_perm_applicable(perm):
		return perm.role in roles and cint(perm.permlevel) == 0

	def has_permission_without_if_owner_enabled(ptype):
		return any(p.get(ptype, 0) and not p.get("if_owner", 0) for p in applicable_permissions)

	applicable_permissions = list(
		filter(is_perm_applicable, getattr(meta, "permissions", []))
	)
	has_if_owner_enabled = any(p.get("if_owner", 0) for p in applicable_permissions)

	perms = frappe._dict(if_owner={})
	perms["has_if_owner_enabled"] = has_if_owner_enabled

	for ptype in frappe.permissions.rights:
		pvalue = any(p.get(ptype, 0) for p in applicable_permissions)
		# check if any perm object allows perm type
		perms[ptype] = cint(pvalue)
		if (
			pvalue
			and has_if_owner_enabled
			and not has_permission_without_if_owner_enabled(ptype)
			and ptype != "create"
		):
			perms["if_owner"][ptype] = cint(pvalue and is_owner)
			# has no access if not owner
			# only provide select or read access so that user is able to at-least access list
			# (and the documents will be filtered based on owner sin further checks)
			perms[ptype] = 1 if ptype in ("select", "read") else 0

	# frappe.local.role_permissions[cache_key] = perms
	return perms


def to_permission_type(ptype) -> viewable_type:
	if ptype == 'create': return 'addible'
	if ptype == 'delete': return 'deletable'
	if ptype == 'write': return 'editable'
	if ptype == 'submit': return 'editable'
	if ptype == 'cancel': return 'editable'
	return 'viewable'

def _has_permission_by_organization(
	meta, organization, user=None, is_owner=None, ptype = '',
):
	perm = _get_user_permissions_in_organization(
		meta,
		organization,
		user,
		is_owner,
		to_permission_type(ptype)
	)
	if perm == None: return True
	if perm.get(ptype, False): return True
	if not is_owner: return False
	p = perm.get('if_owner')
	if isinstance(p, dict) and p.get(ptype, False): return True
	return False


def has_permission(doc: Document, ptype, user, organization_field = 'organization'):
	if user == 'Administrator': return
	organization = doc.get(organization_field)
	is_owner = (doc.get("owner") or "").lower() == user.lower()

	if organization and not _has_permission_by_organization(
		doc.meta,
		organization,
		user,
		is_owner,
		ptype,
	): return False

	if to_permission_type(ptype)  != 'editable': return

	last_organization = (last := doc.get_latest()) and last.get(organization_field)
	if last_organization == organization: return

	if last_organization and not _has_permission_by_organization(
		doc.meta,
		last_organization,
		user,
		is_owner,
		'delete',
	): return False
	if organization and not _has_permission_by_organization(
		doc.meta,
		organization,
		user,
		is_owner,
		'create',
	): return False


@frappe.whitelist()
def viewable():
	if "System Manager" in frappe.get_roles():
		return frappe.get_all(
			TianjyOrganization.DOCTYPE,
			fields=["name", "parent_organization as parent", "label"],
			order_by="lft",
		)
	return frappe.get_all(
		TianjyOrganization.DOCTYPE,
		filters=dict(name=('in', get_user_organizations(type="viewable"))),
		fields=["name", "parent_organization as parent", "label"],
		order_by="lft"
	)
