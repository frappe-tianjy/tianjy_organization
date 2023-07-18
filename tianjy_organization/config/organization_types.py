from frappe import _dict
types = [
	_dict(
		name="Company",
		parent_types=[_dict(type="Company"),],
		leader_types=[],
		root_only=1,
		visible_to_descendants=1,
	), _dict(
		name="Project",
		parent_types=[_dict(type="Company"),],
		leader_types=[],
		root_only=0,
		visible_to_descendants=1,
	), _dict(
		name="Department",
		parent_types=[_dict(type="Project"), _dict(type="Company"), _dict(type="Department")],
		leader_types=[_dict(type="Project")],
		root_only=0,
		visible_to_descendants=1,
	),
]
