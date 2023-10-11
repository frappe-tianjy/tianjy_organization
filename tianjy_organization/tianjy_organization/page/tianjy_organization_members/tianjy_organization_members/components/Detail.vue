<template>
	<div class="form-container">
		<FormDetail 
			:loading="loading"
			v-if="meta&&detail"
			:meta="meta"
			:options="{}"
			:value="detail"
			isHideClose
		></FormDetail>
	</div>
</template>

<script setup lang='ts'>
	import { ref, watch, shallowRef } from 'vue';
	import FormDetail from '../../../../../../../guigu/guigu/public/js/FormDetail'

	const meta = shallowRef<locals.DocType>();

	interface Props{
		doctype:string,
		name?:string
	}
	const props = defineProps<Props>();
	const detail = ref<any>()
	const loading = ref<boolean>(false)
	watch(()=>props.doctype,()=>{
		getMeta(props.doctype)
	},{immediate:true})
	watch(()=>props.name, ()=>{
		getDetail()
	}, {immediate:true})
	async function getDetail(){
		loading.value=true
		if(!props.name){
			detail.value = undefined;
			loading.value=false
			return;
		}
		detail.value = await frappe.db.get_doc(props.doctype, props.name);
		loading.value=false
	}
	async function getMeta(doctype: string) {
		if (!doctype) { return; }
		let local_meta = frappe.get_meta(doctype);
		if (local_meta) {
			local_meta.hide_toolbar = true
			meta.value = local_meta;
			return;
		}
		await frappe.model.with_doctype(doctype);
		local_meta = frappe.get_meta(doctype);
		local_meta!.hide_toolbar = true
		meta.value = local_meta || undefined;
	}
</script>

<style lang='less' scoped>
.form-container{
	border:1px solid #eee;
	:deep(.form-section .form-column:first-child){
		padding-left: 15px;
	}
	.placeholder{
		height: 500px;
		line-height: 500px;
		text-align: center;
	}
}
</style>
