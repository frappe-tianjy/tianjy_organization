const old_set_fieldtype = frappe.ui.filter_utils.set_fieldtype;


const organization_link_filter_operators = [
	'organization',
	'not organization',
	'organization ancestors',
	'not organization ancestors',
	'organization descendants',
	'not organization descendants',
];
const organization_multiselect_filter_operators = [
	'organizations',
	'not organizations',
];
const module_link_filter_operators = [
	'enabled organization module',
	'disabled organization module',
];
const module_multiselect_filter_operators = [
	'enabled organization modules',
	'disabled organization modules',
];

const multiselect_filter_operators = [
	...organization_multiselect_filter_operators,
	...module_multiselect_filter_operators,
];
const module_filter_operators = [
	...module_link_filter_operators,
	...module_multiselect_filter_operators,
];
const filter_operators = [
	...organization_link_filter_operators,
	...organization_multiselect_filter_operators,
	...module_link_filter_operators,
	...module_multiselect_filter_operators,
];

frappe.ui.filter_utils.set_fieldtype = function set_fieldtype(df, fieldtype, condition) {
	if (!fieldtype && (df.original_type || df.fieldtype) === 'Link' && filter_operators.includes(condition)) {
		if (!df.original_options) {
			df.original_options = df.options;
		}
		if (df.original_type) { df.fieldtype = df.original_type; }
		else { df.original_type = df.fieldtype; }

		if (multiselect_filter_operators.includes(condition)) {
			df.fieldtype = 'MultiLink';
		}

		df.description = '';
		df.reqd = 0;
		df.ignore_link_validation = true;
		df.options = 'Tianjy Organization';
		if (module_filter_operators.includes(condition)) {
			df.options = 'Tianjy Organization Module';
		}
		return;
	}
	old_set_fieldtype.call(this, df, fieldtype, condition);
};
