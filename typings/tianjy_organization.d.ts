import * as store from '../tianjy_organization/public/js/store'
declare global {
	export namespace frappe {
		/** @deprecated frappe.tianjy.organization */
		export const tianjyOrganization = store;
		export namespace tianjy {
			export {store as organization};
		}
	}
}
