export default function getLink(
	data?: Record<string, any>,
	meta?: locals.DocType,
	linkField?: string
): [string, string] | undefined {
	if (!data) { return; }
	if (!meta) { return; }
	if (!linkField) { return; }
	const { fields } = meta;
	if (!fields) { return; }

	const link = data[linkField];
	const name = typeof link === 'string' && link;
	if (!name) { return; }

	const field = fields.find(v => v.fieldname === linkField);
	if (!field) { return; }
	const option = field.options;
	if (!option) { return; }

	if (field.fieldtype === 'Link') { return [option, name]; }

	if (field.fieldtype !== 'Dynamic Link') { return; }
	const dynamicLinkField = fields.find(v => v.fieldname === option);
	if (!dynamicLinkField) { return; }
	if (dynamicLinkField.fieldtype !== 'Link') { return; }
	if (dynamicLinkField.options !== 'DocType') { return; }
	const doctype = data[option];
	if (typeof doctype !== 'string' || !doctype) { return; }
	return [doctype, name];
}
