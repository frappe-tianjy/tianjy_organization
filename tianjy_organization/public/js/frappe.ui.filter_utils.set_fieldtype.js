const old_set_fieldtype = frappe.ui.filter_utils.set_fieldtype;


const link_filter_operators = [
	'organization',
	'not organization',
	'organization ancestors',
	'not organization ancestors',
	'organization descendants',
	'not organization descendants',
];
const multiselect_filter_operators = [
	'organizations',
	'not organizations',
];

const filter_operators = [...link_filter_operators, ...multiselect_filter_operators];

frappe.ui.filter_utils.set_fieldtype = function set_fieldtype(df, fieldtype, condition) {
	if (!fieldtype && (df.original_type || df.fieldtype) === 'Link' &&filter_operators.includes(condition)) {
		if (df.original_type) { df.fieldtype = df.original_type; }
		else { df.original_type = df.fieldtype; }

		if (multiselect_filter_operators.includes(condition)) {
			df.fieldtype = 'MultiLink';
		}

		df.description = '';
		df.reqd = 0;
		df.ignore_link_validation = true;
		df.options = 'Tianjy Organization';

		return;
	}
	old_set_fieldtype.call(this, df, fieldtype, condition);
};