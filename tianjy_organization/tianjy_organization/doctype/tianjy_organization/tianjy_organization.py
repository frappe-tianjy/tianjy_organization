# Copyright (c) 2023, 天玑 Tinajy and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.cache_manager import clear_user_cache
from frappe.utils.nestedset import NestedSet
from frappe.query_builder.utils import DocType
from frappe.utils.nestedset import validate_loop

from ..tianjy_organization_type.tianjy_organization_type import TianjyOrganizationType


@frappe.whitelist()
def get_type(type=''):
	type = frappe.get_doc(TianjyOrganizationType.DOCTYPE, type)
	return dict(
		name=type.name,
		parent_types=[type.type for type in type.parent_types],
		doc_types=[type.doc_type for type in type.doc_types],
		root_only=bool(type.root_only),
		no_workspace=bool(type.no_workspace),
	)


class TianjyOrganization(NestedSet):
	DOCTYPE = "Tianjy Organization"

	@classmethod
	def find(cls, name: str) -> 'TianjyOrganization | None':
		try:
			return frappe.get_doc(cls.DOCTYPE, name)
		except:
			return

	def on_trash(self, allow_root_deletion=False):
		return super().on_trash(True)
		# TODO: 删除成员信息

	def after_delete(self):
		frappe.db.delete("DefaultValue", dict(
			defkey='tianjy_organization',
			defvalue=self.name
		))
		clear_user_cache()


@frappe.whitelist()
def sort(organization: str, target: str, before = False, children = False):
	doctype = TianjyOrganization.DOCTYPE
	meta = frappe.get_meta(doctype)
	parent_field = meta.nsm_parent_field
	if not parent_field: return False
	if isinstance(children, str): children = json.loads(children)
	if isinstance(before, str): before = json.loads(before)
	parent_name = target if children else frappe.db.get_value(doctype, target, parent_field, for_update=True)
	Table = DocType(doctype)
	doc = TianjyOrganization.find(organization)

	if parent_name:
		left, right = frappe.db.get_value(doctype, {"name": parent_name}, ["lft", "rgt"], for_update=True)
		validate_loop(doc.doctype, doc.name, left, right)


	# 处理当前节点及后代节点的 lft 及 rgt，将其修改为从 -1 递减
	frappe.qb.update(Table).set(Table.lft, doc.lft - 1 - Table.lft).set(Table.rgt, doc.lft - 1 - Table.rgt).where(
		(Table.lft >= doc.lft) & (Table.rgt <= doc.rgt)
	).run()

	# 将后部节点向前移动，填补点钱节点及后代节点位置
	diff = doc.rgt - doc.lft + 1
	frappe.qb.update(Table).set(Table.lft, Table.lft - diff).set(Table.rgt, Table.rgt - diff).where(
		Table.lft > doc.rgt
	).run()

	# 将祖先节点的 rgt 修正，填补位置
	frappe.qb.update(Table).set(Table.rgt, Table.rgt - diff).where(
		(Table.lft < doc.lft) & (Table.rgt > doc.rgt)
	).run()

	# re-query value due to computation above
	new_parent = (
		frappe.qb.from_(Table)
		.select(Table.lft, Table.rgt)
		.where(Table.name == parent_name)
		.for_update()
		.run(as_dict=True)[0]
	) if parent_name else None
	if new_parent:
		# set parent lft, rgt
		frappe.qb.update(Table).set(Table.rgt, Table.rgt + diff).where(Table.name == parent_name).run()
		# shift right rgts of ancestors whose only rgts must shift
		frappe.qb.update(Table).set(Table.rgt, Table.rgt + diff).where(
			(Table.lft < new_parent.lft) & (Table.rgt > new_parent.rgt)
		).run()

	sql = frappe.qb.update(Table).set(Table.lft, Table.lft + diff).set(Table.rgt, Table.rgt + diff)
	# shift right at new parent
	if new_parent and children:
		if before:
			sql = sql.where(Table.lft > new_parent.lft)
			new_diff = new_parent.lft
		else:
			sql = sql.where(Table.lft > new_parent.rgt)
			new_diff = new_parent.rgt - 1
	else:
		target_data = (
			frappe.qb.from_(Table)
			.select(Table.lft, Table.rgt)
			.where(Table.name == target)
			.for_update()
			.run(as_dict=True)[0]
		)
		if before:
			sql = sql.where(Table.lft > target_data.lft - 1)
			new_diff = target_data.lft - 1
		else:
			sql = sql.where(Table.lft > target_data.rgt)
			new_diff = target_data.rgt
	sql.run()

	# 移动到正确位置，
	sql = frappe.qb.update(Table).set(Table.lft, -Table.lft + new_diff).set(
		Table.rgt, -Table.rgt + new_diff
	)
	sql.where(Table.lft < 0).run()


	(frappe.qb.update(Table)
		.set(Table[parent_field], parent_name)
		.where(Table.name == organization)
	).run()
