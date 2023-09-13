<template>
	<Page>
		<template #title>
			<div>组织设置</div>
		</template>
		<template #sider>
			<OrganizationTree 
				v-model="organization"
				:permissions="permissions"
			></OrganizationTree>
		</template>
		<el-tabs v-model="activeName" class="organization-tabs">
			<el-tab-pane label="基本信息" name="info">
				<FormDetail :name="organization?.name" doctype="Tianjy Organization"></FormDetail>
			</el-tab-pane>
			<el-tab-pane class="workspace" label="工作区" name="workspace">
				<Workspace v-if="organization" :organization="organization.name"></Workspace>
			</el-tab-pane>
			<el-tab-pane class="member" label="成员" name="users">
				<Member v-if="organization" :organization="organization.name"></Member>
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
const meta = ref<locals.DocType>();

onMounted(()=>getMeta())
async function getMeta() {
	let local_meta = frappe.get_meta('Tianjy Organization');
	if (local_meta) {
		meta.value = local_meta;
		return;
	}
	await frappe.model.with_doctype('Tianjy Organization');
	local_meta = frappe.get_meta('Tianjy Organization');
	meta.value = local_meta || undefined;
}
const permissions = computed(() => {
	if (!meta.value) {
		return { deletePermission: false, createPermission: false, writePermission:false };
	}
	const deletePermission = frappe.perm.has_perm(meta.value.name, 0, 'delete');
	const createPermission = frappe.perm.has_perm(meta.value.name, 0, 'create');
	const writePermission = frappe.perm.has_perm(meta.value.name, 0, 'write');
	return { deletePermission, createPermission, writePermission };
});
</script>

<style lang='less' scoped>
.organization-tabs{
	height: 100%;
    display: flex;
    flex-direction: column;
}
.workspace, .member{
	height: 100%;
}
</style>
