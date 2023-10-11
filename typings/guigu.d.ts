import * as store from '../tianjy_organization/public/js/store'
declare global {
	namespace frappe{
		export {store as tianjyOrganization};
	}
}
