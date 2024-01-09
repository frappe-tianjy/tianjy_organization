<template>
	<Main
		v-if="value && docMeta && name"
		:key="`${docMeta.name}:${value.name}`"
		:meta="docMeta"
		:options="options"
		:loading="loading"
		:name="name"
		:isHideClose="isHideClose"
		v-model:value="doc"
		@refresh="refresh" />
</template>
<script lang="ts" setup>
import { computed, shallowRef, watch } from 'vue';

import getLink from './getLink';
import Main from './Main.vue';

defineOptions({ name: 'FormDetail:Root', inheritAttrs: false });
const props = defineProps<{
	/** 当前 doctype 的信息 */
	meta: locals.DocType
	/** 数据选项 */
	options: Record<string, any>;

	/** 主区域的 value */
	value?: any;

	/** 主区域数据是否在加载中 */
	loading?: boolean;


	linkField?: string;
	isHideClose?: boolean
}>();
const emit = defineEmits<{
	(event: 'refresh'): void;
	(event: 'update:value', value?: any): void;
}>();
function refresh() {
	emit('refresh');
}
const doc = computed({
	get: () => props.value,
	set: v => emit('update:value', v),
});
let docMetaLoadingDoctype = '';
let DocTypeLoadingId = 0;
const linkField = computed(() => props.linkField);
const docMetaLoading = shallowRef<locals.DocType>();

const link = computed(() => getLink(doc.value, props.meta, linkField.value));
const name = computed(() => link.value?.[1] || doc.value?.name);
watch(() => link.value?.[0], doctype => {
	if (!doctype) { return; }
	if (doctype === docMetaLoadingDoctype) { return; }
	docMetaLoadingDoctype = doctype;
	docMetaLoading.value = undefined;
	DocTypeLoadingId++;
	const id = DocTypeLoadingId;
	(async () => {
		await new Promise(r => frappe.model.with_doctype(doctype, r));
		const meta = frappe.get_doc('DocType', doctype);
		if (id !== DocTypeLoadingId) { return; }
		if (docMetaLoadingDoctype !== doctype) { return; }
		docMetaLoading.value = meta || undefined;
	})();
}, { immediate: true });
const docMeta = computed(() => {
	const doctype = link.value?.[0];
	if (!doctype) { return props.meta; }
	if (doctype !== docMetaLoadingDoctype) {
		return;
	}
	return docMetaLoading.value;
});

</script>
