// 增加当前组织的

import * as store from './store';


const old = frappe.request.prepare;
frappe.request.prepare = function (opts) {
	old.call(this, ...arguments);
	const organization = store.getCurrent();
	if (!organization) { return; }
	if (opts.headers) {
		opts.headers['X-Tianjy-Organization'] = organization;
	} else {
		opts.headers = {'X-Tianjy-Organization': organization};
	}
};
