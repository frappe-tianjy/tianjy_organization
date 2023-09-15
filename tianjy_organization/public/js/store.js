// @ts-check

const key = 'TianjyOrganization/currentOrganization';

export function getCurrent() {
	return localStorage.getItem(key) || '';
}
/**
 *
 * @param {string} v
 */
export function setCurrent(v) {
	localStorage.setItem(key, v || '');
}
