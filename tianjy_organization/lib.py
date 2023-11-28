import frappe
from frappe.exceptions import DoesNotExistError

from .tianjy_organization.doctype.tianjy_organization.tianjy_organization import TianjyOrganization
from .tianjy_organization.doctype.tianjy_organization_member.tianjy_organization_member import TianjyOrganizationMember
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



def has_sync_permission() -> bool:
	all_roles = frappe.get_roles()
	if 'System Manager' in all_roles: return True
	return False

@frappe.whitelist()
def sync_roles_to_organization(organization: str | list[str] | None = None):

	if not has_sync_permission(): return
	# import frappe.db
	if not organization:
		filters = {}
	elif isinstance(organization, list):
		filters = {'name': ('in', organization)}
	elif isinstance(organization, str):
		filters = {'name': organization}
	else:
		return
	from .tianjy_organization.doctype.tianjy_organization.tianjy_organization import TianjyOrganization
	organizations = frappe.get_all(TianjyOrganization.DOCTYPE, filters=filters, pluck="name")
	if not organizations: return
	from .tianjy_organization.doctype.tianjy_organization_role.tianjy_organization_role import TianjyOrganizationRole
	from .tianjy_organization.doctype.tianjy_organization_member.tianjy_organization_member import TianjyOrganizationMember

	from frappe.query_builder.utils import DocType

	frappe.db.delete(TianjyOrganizationRole.DOCTYPE, {'organization': ('in', organizations)})


	MemberTable = DocType(TianjyOrganizationMember.DOCTYPE)
	user_organizations = frappe.qb.from_(MemberTable).select('user', 'organization').where(
		MemberTable.organization.isin(organizations) &
		(MemberTable.is_inherit == 0)
	).run(as_dict=True)

	users = list(set([v.get('user') for v in user_organizations]))
	if not users: return
	user_roles = frappe.get_all('Has Role', filters={
		'parenttype': 'User',
		'parent': ('in', users),
	}, fields=['parent', 'role'])
	roles: dict[str, set[str]] = {}
	for u in user_roles:
		user = u.get('parent')
		role = u.get('role')
		l = roles.get(user, None)
		if l:
			l.add(role)
		else:
			roles[user] = set([role])
	if not roles: return

	q = frappe.qb.into(DocType(TianjyOrganizationRole.DOCTYPE))
	q = q.columns('name', 'user', 'organization', 'role')
	for v in user_organizations:
		user = v.get('user')
		organization = v.get('organization')
		for role in roles.get(user, []):
			q = q.insert(frappe.generate_hash(), user, organization, role)
	q.run()


@frappe.whitelist()
def viewable():
	organizations = frappe.get_all(
		TianjyOrganization.DOCTYPE,
		filters=dict(
			name=('in', get_user_organizations(type="viewable"))
		),
		fields=["name", "parent_organization as parent", "label"],
		order_by="lft"
	)
	if not organizations: return []
	default_member = TianjyOrganizationMember.find_default(frappe.session.user)
	print(default_member)
	if not default_member: return organizations
	default_organization = default_member.organization
	for organization in organizations:
		if organization.name == default_organization:
			organization['default'] = 1
			break
	return organizations

@frappe.whitelist()
def set_default(organization):
	member = TianjyOrganizationMember.find(frappe.session.user, organization, True)
	if not member: return False
	member.update({'default': 1})
	member.save(ignore_permissions=True)
	return True
