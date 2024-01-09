import './selector';
import './toHome';
import './pages';
import './frappe.ui.filter_utils.set_fieldtype';
import './frappe.request.prepare';
import './frappe.views.Workspace.prototype.append_item';

import * as store from './store';
import './patches';
frappe.provide('frappe.tianjy');
Object.defineProperty(frappe.tianjy, 'organization', {
	get() { return store; },
	set() { },
	configurable: true,
	enumerable: true,
});

Object.defineProperty(frappe, 'tianjyOrganization', {
	get() {
		console.warn('frappe.tianjyOrganization 已经过时，请用 frappe.tianjy.organization 代替');
		return store;
	},
	set() { },
	configurable: true,
	enumerable: true,
});
