<template>
	<div
		ref="wrapperRef"
		class="content page-container"
		id="page-Workspaces"
		data-page-route="Workspaces"
	>
	</div>
</template>

<script setup lang='ts'>
import { ref, watch } from 'vue';

import Workspace from './workspace.js';

interface Props{
	organization:string
}
const props = defineProps<Props>();
const wrapperRef = ref<HTMLElement>();

watch([wrapperRef, ()=>props.organization], (_, org)=>{
	if (!wrapperRef.value||!props.organization){ return; }
	wrapperRef.value.innerHTML = '';
	frappe.ui.make_app_page({
		parent: wrapperRef.value,
		name: 'Workspaces',
		title: __('Workspace'),
	});
	const workspace = new Workspace(wrapperRef.value, props.organization);
	workspace.show();
}, {immediate: true});
</script>

<style lang='less' scoped>
.content{
	height: 100%;
    display: flex;
    flex-direction: column;
	:deep(.page-body){
		overflow: auto;
	}
	:deep(.page-head){
		position: static;
	}
}
</style>
