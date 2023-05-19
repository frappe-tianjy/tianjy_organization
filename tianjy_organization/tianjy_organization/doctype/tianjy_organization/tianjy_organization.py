# Copyright (c) 2023, 天玑 Tinajy and contributors
# For license information, please see license.txt

# import frappe
from frappe.utils.nestedset import NestedSet

from typing import Any
import frappe
from frappe.utils.nestedset import NestedSet
from ....config.organization_types import types


type_list: list[str] = [t.name for t in types if t.visible_to_descendants]

@frappe.whitelist()
def get_types(type = ''):
	# TODO: 从独立的列表中读取
	return [dict(
		name=type.name,
		parent_types=[type.type for type in type.parent_types],
		leader_types=[type.type for type in type.leader_types],
		root_only=bool(type.root_only)
	) for type in types]


class TianjyOrganization(NestedSet):
	DOCTYPE="Tianjy Organization"
	@classmethod
	def find(cls, name: str) -> 'TianjyOrganization | None':
		try:
			return frappe.get_doc(cls.DOCTYPE, name)
		except:
			return
