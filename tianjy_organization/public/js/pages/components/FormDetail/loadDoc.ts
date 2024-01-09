export default async function loadDoc(
	doctype: string,
	name: string,
) {

	const doc = frappe.get_doc(doctype, name);
	if (
		doc &&
		frappe.model.get_docinfo(doctype, name) &&
		(doc.__islocal || frappe.model.is_fresh(doc))
	) { return true; }
	return new Promise<boolean>(resolve => {
		frappe.model.with_doc(doctype, name, (name, r) => {
			if (r && r['403']) { return resolve(false); }

			if (!(locals[doctype] && locals[doctype][name])) {
				return resolve(false);
			}
			resolve(true);
		});
	});
}
