import { ref } from 'vue';

const mQuery = window.matchMedia('(max-width: 640px)');
/** @type {import('vue').Ref<boolean>?} */
let smallMeta = null;
function mediaChange() {
	smallMeta.value = Boolean(mQuery.matches);
}
/** @returns {import('vue').Ref<boolean>} */
export default function useMetaQuery() {
	if (!smallMeta) {
		smallMeta = ref(mQuery.matches);
		mQuery.addEventListener('change', mediaChange);
	}
	return smallMeta;
}
