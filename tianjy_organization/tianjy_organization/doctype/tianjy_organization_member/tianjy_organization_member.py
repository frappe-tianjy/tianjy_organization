# Copyright (c) 2023, 天玑 Tinajy and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document
from frappe.query_builder.utils import DocType

from ..tianjy_organization_inheritable.tianjy_organization_inheritable import TianjyOrganizationInheritable
from ..tianjy_organization_role.tianjy_organization_role import TianjyOrganizationRole

@frappe.whitelist()
def get_user_organization_roles(user, organization):
	return frappe.get_all(
		TianjyOrganizationRole.DOCTYPE,
		filters=dict(user=user, organization=organization),
		pluck="role"
	)



@frappe.whitelist()
def set_user_organization_roles(user, organization, roles):
	doc = TianjyOrganizationMember.find(user, organization)
	if doc:
		doc.check_permission('write')
		if isinstance(roles, str): roles = json.loads(roles)
	elif not doc:
		roles = []

	old_roles = get_user_organization_roles(user, organization)
	need_remove = set(old_roles) - set(roles)
	need_add = (set(roles) - set(old_roles)) & set(get_all_roles())
	if need_remove:
		frappe.db.delete(TianjyOrganizationRole.DOCTYPE, dict(
			user=user,
			organization=organization,
			role=('in', need_remove)
		))

	if need_add:
		q = frappe.qb.into(DocType(TianjyOrganizationRole.DOCTYPE))
		q = q.columns('name', 'user', 'organization', 'role')
		for role in need_add:
			q = q.insert(frappe.generate_hash(), user, organization, role)
		q.run()

def get_all_roles():
	active_domains = frappe.get_active_domains()

	return frappe.get_all(
		"Role",
		filters={"name": ("not in", "Administrator,Guest,All"), "disabled": 0},
		or_filters={"ifnull(restrict_to_domain, '')": "", "restrict_to_domain": ("in", active_domains)},
		pluck="name"
	)


def inheritable_on_update(inheritable, method):
	inherit_from = inheritable.inherit_from
	organization = inheritable.organization

	frappe.db.delete(TianjyOrganizationMember.DOCTYPE, filters=dict(
		organization=organization,
		inherit_from=inherit_from
	));

	members = frappe.get_all(
		TianjyOrganizationMember.DOCTYPE,
		fields=['visible', 'viewable', 'addible', 'editable', 'deletable', 'manageable', 'user'],
		filters=dict(organization=inherit_from, inherit_from=inherit_from)
	)
	if not members: return
	visible = inheritable.visible
	viewable = inheritable.viewable
	addible = inheritable.addible
	editable = inheritable.editable
	deletable = inheritable.deletable
	manageable = inheritable.manageable

	Table = DocType(TianjyOrganizationMember.DOCTYPE)
	insert_qb = frappe.qb.into(Table)
	insert_qb = insert_qb.columns(
		'name', 'user', 'organization', 'inherit_from', 'is_inherit',
		'visible', 'viewable', 'addible', 'editable', 'deletable', 'manageable'
	)
	for member in members:
		user = member['user']
		name = f'{inherit_from}:{organization}/{user}'
		insert_qb = insert_qb.insert(
			name, user, organization, inherit_from, 1,
			1 if visible and member['visible'] else 0,
			1 if viewable and member['viewable'] else 0,
			1 if addible and member['addible'] else 0,
			1 if editable and member['editable'] else 0,
			1 if deletable and member['deletable'] else 0,
			1 if manageable and member['manageable'] else 0,
		)
	insert_qb.run()

def inheritable_on_trash(inheritable, method):
	frappe.db.delete(TianjyOrganizationMember.DOCTYPE, filters=dict(
		organization=inheritable.organization,
		inherit_from=inheritable.inherit_from
	));

class TianjyOrganizationMember(Document):
	DOCTYPE="Tianjy Organization Member"
	@classmethod
	def find(cls, user, organization) -> 'TianjyOrganizationMember | None':
		try:
			return frappe.get_last_doc(cls.DOCTYPE, filters=dict(
				user=user,
				organization=organization,
				inherit_from=organization,
			)) # type: ignore
		except frappe.exceptions.DoesNotExistError:
			return None

	def before_validate(self):
		if self.is_new():
			self.inherit_from = self.organization # type: ignore
			self.is_inherit = 0
	def validate(self):
		if self.inherit_from != self.organization: # type: ignore
			return frappe.throw('无法修改通过继承的配置')

	def before_save(self):
		viewable = self.viewable # type: ignore
		if viewable:
			self.visible = viewable
		else:
			self.addible = viewable
			self.editable = viewable
			self.deletable = viewable
	def on_update(self):
		Table = DocType(self.DOCTYPE)
		user = self.user # type: ignore
		inherit_from = self.organization # type: ignore
		frappe.db.delete(self.DOCTYPE, filters=dict(
			user=user,
			inherit_from=inherit_from,
			organization=('!=', inherit_from),
		));


		organizations = frappe.get_all(
			TianjyOrganizationInheritable.DOCTYPE,
			fields=['visible', 'viewable', 'addible', 'editable', 'deletable', 'manageable', 'organization'],
			filters=dict(inherit_from=inherit_from)
		)
		if not organizations: return

		visible = self.visible
		viewable = self.viewable # type: ignore
		addible = self.addible
		editable = self.editable
		deletable = self.deletable
		manageable = self.manageable # type: ignore

		insert_qb = frappe.qb.into(Table)
		insert_qb = insert_qb.columns(
			'name', 'user', 'organization', 'inherit_from', 'is_inherit',
			'visible', 'viewable', 'addible', 'editable', 'deletable', 'manageable'
		)
		for inheritable in organizations:
			organization = inheritable['organization']
			name = f'{inherit_from}:{organization}/{user}'
			insert_qb = insert_qb.insert(
				name, user, organization, inherit_from, 1,
				1 if visible and inheritable['visible'] else 0,
				1 if viewable and inheritable['viewable'] else 0,
				1 if addible and inheritable['addible'] else 0,
				1 if editable and inheritable['editable'] else 0,
				1 if deletable and inheritable['deletable'] else 0,
				1 if manageable and inheritable['manageable'] else 0,
			)
		insert_qb.run()



	def on_trash(self, allow_root_deletion=False):
		frappe.db.delete(self.DOCTYPE, filters=dict(
			inherit_from=self.organization, # type: ignore
			user=self.user, # type: ignore
		));
