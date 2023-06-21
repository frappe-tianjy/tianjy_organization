// @ts-check
const packageName = 'frappe.core.doctype.session_default_settings.session_default_settings';
const getMethod = `${packageName}.get_session_default_values`;
const setMethod = `${packageName}.set_session_default_values`;

/**
 *
 * @param {string} tianjy_organization
 */
export default async function setOrganization(tianjy_organization) {
	const data = await frappe.call({ method: getMethod });

	/** @type {{ fieldname: string, default?: string; }[]} */
	const fields = JSON.parse(data?.message || '[]');

	const values = Object.fromEntries(fields.map(v => [v.fieldname, v.default || '']));
	values.tianjy_organization = tianjy_organization;

	/** @type {{ message: string }?} */
	const result = await frappe.call({
		method: setMethod, args: { default_values: values },
	});

	if (result?.message === 'success') {
		frappe.show_alert({
			message: __('Session Defaults Saved'),
			indicator: 'green',
		});
		frappe.assets.clear_local_storage();
		Promise.all([
			tianjy_organization ? frappe.call('tianjy_organization.lib.get_default_workspace', {
				organization: tianjy_organization,
			}).then(v => v?.message) : '',
			frappe.xcall('frappe.sessions.clear').then(message => {
				frappe.show_alert({
					message,
					indicator: 'info',
				});
			}),
		]).then(([workspace]) => {
			if (!workspace) {
				location.reload();
				return;
			}
			location.href = `/app/${encodeURIComponent(workspace)}`;
		}, () => {
			location.reload();
		});
	} else {
		frappe.show_alert({
			message: __('An error occurred while setting Session Defaults'),
			indicator: 'red',
		});
	}
}
