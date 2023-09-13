<template>
	<Page>
		<template #title>
			<div>组织设置</div>
		</template>
		<template #sider>
			<OrganizationTree 
				v-model="organization"
				:permissions="organizationPermissions"
			></OrganizationTree>
		</template>
		<el-tabs v-model="activeName" class="organization-tabs">
			<el-tab-pane class="tab-container" label="基本信息" name="info">
				<FormDetail :name="organization?.name" doctype="Tianjy Organization"></FormDetail>
			</el-tab-pane>
			<el-tab-pane class="tab-container" label="工作区" name="workspace">
				<Workspace v-if="organization" :organization="organization.name"></Workspace>
			</el-tab-pane>
			<el-tab-pane class="tab-container" label="成员" name="users">
				<Member v-if="organization" :organization="organization.name" :permissions="memberPermissions"></Member>
			</el-tab-pane>
		</el-tabs>
	</Page>
</template>

<script setup lang='ts'>
import { computed, onMounted, ref } from 'vue';
import Page from '../../../../../../guigu_pm/guigu_pm/public/js/components/page/index.vue';
import OrganizationTree from './components/OrganizationTree.vue'
import type { Organization, OrganizationType } from './type';
import FormDetail from './components/Detail.vue'
import Workspace from './components/Workspace.vue'
import Member from './components/Member.vue'

interface Props{

}
const props = defineProps<Props>();
interface Emit{

}
const emit = defineEmits<Emit>();
const organization = ref<Organization>();
const activeName = ref<string>('info');
const organizationMeta = ref<locals.DocType>();
const memberMeta = ref<locals.DocType>();

onMounted(async()=>{
	organizationMeta.value = await getMeta('Tianjy Organization')
	memberMeta.value = await getMeta('Tianjy Organization Member')
})
async function getMeta(doctype:string) {
	let local_meta = frappe.get_meta(doctype);
	if (local_meta) {
		return local_meta;
	}
	await frappe.model.with_doctype(doctype);
	return frappe.get_meta(doctype)||undefined;
}

function getPermission(meta?:locals.DocType){
	if (!meta) {
		return { deletePermission: false, createPermission: false, writePermission:false };
	}
	const deletePermission = frappe.perm.has_perm(meta.name, 0, 'delete');
	const createPermission = frappe.perm.has_perm(meta.name, 0, 'create');
	const writePermission = frappe.perm.has_perm(meta.name, 0, 'write');
	return { deletePermission, createPermission, writePermission };
}
const organizationPermissions = computed(() => {
	return getPermission(organizationMeta.value)
});
const memberPermissions = computed(() => {
	return getPermission(memberMeta.value)
});
</script>

<style lang='less' scoped>
.organization-tabs{
	height: 100%;
    display: flex;
    flex-direction: column;
}
.tab-container{
	height: 100%;
}
</style>
