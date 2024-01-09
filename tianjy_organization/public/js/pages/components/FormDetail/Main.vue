<template>
	<div ref="root">
		<Header v-model:open="open" :hasSider="!single_column" :isHideClose="isHideClose" @hide="hide" />
		<div class="container page-body">
			<div class="page-toolbar hide">
				<div class="container">
				</div>
			</div>
			<div class="page-wrapper">
				<div class="page-content">
					<div class="workflow-button-area btn-group pull-right hide">
					</div>
					<div class="clearfix"></div>
					<div class="row layout-main">
						<div class="col layout-main-section-wrapper">
							<div class="layout-main-section">
								<div>
									<div class="std-form-layout">
										<div class="form-layout">
											<div class="form-message hidden" />
											<div class="form-page" />
										</div>
									</div>
								</div>
							</div>
							<div class="layout-footer hide" />
						</div>
						<div v-if="!single_column" :hidden="!open"
							class="col-lg-2 layout-side-section" />
					</div>
				</div>
			</div>
		</div>
	</div>
</template>
<script lang="ts" setup>
import { computed, shallowRef, onMounted, onUnmounted } from 'vue';
import { useStorage } from '@vueuse/core';

import Header from './Header.vue';
import Form from './Form';
import loadDoc from './loadDoc';
import currentTab from './currentTab';

defineOptions({ name: 'FormDetail' });

const props = defineProps<{
	/** 当前 doctype 的信息 */
	meta: locals.DocType
	/** 数据选项 */
	options: Record<string, any>;

	/** 主区域的 value */
	value: locals.Doctype;
	name: string

	/** 主区域数据是否在加载中 */
	loading?: boolean;
	isHideClose?: boolean
}>();
const emit = defineEmits<{
	(event: 'refresh'): void;
	(event: 'update:value', value?: any): void;
}>();

function hide() {
	emit('update:value');
}

const single_column = computed(() => Boolean(props.meta?.hide_toolbar));

const open = useStorage(`mainView:FormDetail:sider:${props.meta.name}`, true);
const tt = __;

const root = shallowRef();
let layout: Form | undefined;
const onUpdate = ({ doctype, name, modified }: {
	doctype: string;
	name: string;
	modified: string;
}) => {
	if (doctype !== props.meta.name) { return; }
	if (name !== props.name) { return; }
	if (!layout) { return; }

	if (modified === layout.doc.modified) { return; }
	if (layout.is_dirty()) {
		layout.show_conflict_message();
	} else {
		layout.reload_doc();
	}
};
onMounted(() => {
	const body = root.value;
	if (!body) { return; }
	const doctype = props.meta.name;
	const { name } = props;
	loadDoc(doctype, name).then(r => {
		if (!r) { return; }
		layout = new Form(doctype, name, body, hide, currentTab);
		layout.refresh(name);
	});

	frappe.realtime.on('doc_update', onUpdate);
});
onUnmounted(() => {
	frappe.realtime.off('doc_update', onUpdate);
});

</script>
