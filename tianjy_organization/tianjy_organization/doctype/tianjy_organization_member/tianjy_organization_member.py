# Copyright (c) 2023, 天玑 Tinajy and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document
from frappe.query_builder.utils import DocType

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


class TianjyOrganizationMember(Document):
	DOCTYPE="Tianjy Organization Member"
	@classmethod
	def find(cls, user, organization) -> 'TianjyOrganizationMember | None':
		try:
			return frappe.get_last_doc(cls.DOCTYPE, filters=dict(user=user,organization=organization))
		except frappe.exceptions.DoesNotExistError:
			return None

	def before_validate(self):
		user = self.user
		copy_from_organization = self.copy_from
		if not copy_from_organization: return
		if copy_from_organization == self.organization:
			return frappe.throw('不能从自身复制')
		copy_from = TianjyOrganizationMember.find(user, copy_from_organization)
		if not copy_from:
			return frappe.throw('当前用户未在对应复制组织中配置权限')
		if copy_from.copy_from:
			return frappe.throw('不支持从其他被复制项复制')

		if not self.copy_roles_only:
			self.visible = copy_from.visible
			self.viewable = copy_from.viewable
			self.addible = copy_from.addible
			self.editable = copy_from.editable
			self.deletable = copy_from.deletable

		if frappe.get_all(self.DOCTYPE, filters={'user': user, 'copy_from': self.organization}, page_length=1):
			return frappe.throw('存在复制自此项的配置，无法将此项设置为复制')

	def before_save(self):
		viewable = self.viewable
		if viewable:
			self.visible = viewable
		else:
			self.addible = viewable
			self.editable = viewable
			self.deletable = viewable
	def on_update(self):
		Table = DocType(self.DOCTYPE)
		(frappe.qb.update(Table)
			.set(Table.visible, self.visible)
			.set(Table.viewable, self.viewable)
			.set(Table.addible, self.addible)
			.set(Table.editable, self.editable)
			.set(Table.deletable, self.deletable)
			.where((Table.copy_from == self.organization) & (Table.copy_roles_only == 0))
		).run()

	def on_trash(self, allow_root_deletion=False):
		frappe.db.delete(self.DOCTYPE, filters={ 'copy_from': self.organization, 'synchronous_deletion': 1 });
