# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
# Author - Shivam Mishra <shivam@frappe.io>


from pypika import Order
import frappe
from frappe import _
from frappe.desk.desktop import Workspace
from frappe.query_builder.utils import DocType
from . import get_user_organizations

def get_pages(user: str, has_access = False, is_admin = False):
	# don't get domain restricted pages

	Workspace = DocType('Workspace')
	OrganizationWorkspace = DocType('Tianjy Organization Workspace')

	query = frappe.qb.from_(Workspace).select(
		Workspace.name.as_("name"),
		Workspace.title.as_("title"),
		Workspace.for_user.as_("for_user"),
		Workspace.parent_page.as_("parent_page"),
		Workspace.content.as_("content"),
		Workspace.public.as_("public"),
		Workspace.module.as_("module"),
		Workspace.icon.as_("icon"),
		Workspace.is_hidden.as_("is_hidden"),
		OrganizationWorkspace.organization.as_('organization'),
	).left_join(OrganizationWorkspace).on(Workspace.name == OrganizationWorkspace.workspace)

	if not is_admin:
		# TODO: 可以进一步精细控制
		where = (OrganizationWorkspace.organization.isnull()
				| OrganizationWorkspace.organization.isin(get_user_organizations(user, "viewable")))

		if not has_access:
			blocked_modules = frappe.get_doc("User", user).get_blocked_modules()
			blocked_modules.append("Dummy Module")
			where = (
				Workspace.restrict_to_domain.isin(frappe.get_active_domains())
				& Workspace.module.notin(blocked_modules)
				& where
			)
		query = query.where(where)
	query = query.orderby(Workspace.sequence_id, order=Order.asc)
	return query.run(as_dict=True)

@frappe.whitelist()
def get_workspace_sidebar_items():
	"""Get list of sidebar items for desk"""
	user: str = frappe.session.user
	is_admin = "System Manager" in frappe.get_roles()
	has_access = "Workspace Manager" in frappe.get_roles()

	all_pages = get_pages(user, has_access, is_admin)
	pages = []
	private_pages = []

	# Filter Page based on Permission
	for page in all_pages:
		try:
			workspace = Workspace(page, True)
			if has_access or workspace.is_permitted():
				if page.public and (has_access or not page.is_hidden):
					pages.append(page)
				elif page.for_user == user:
					private_pages.append(page)
				page["label"] = _(page.get("name"))
		except frappe.PermissionError:
			pass
	if private_pages:
		pages.extend(private_pages)

	return {"pages": pages, "has_access": has_access}
