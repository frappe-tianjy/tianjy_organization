<template>
	<div v-loading="loading">
		<Page :siderStyle="{width:'550px'}">
			<template #title>
				<div>组织人员</div>
			</template>
			<template #sider>
				<Users 
					v-model:loading="loading"
					v-model="user"
					:permissions="userPermissions"
				></Users>
			</template>
			<el-tabs v-model="activeName" class="user-tabs">
				<el-tab-pane label="基本信息" name="info">
					<FormDetail :name="user?.name" doctype="User"></FormDetail>
				</el-tab-pane>
				<el-tab-pane class="organization" label="组织" name="organization">
					<Organization v-if="user" :permissions="memberPermissions" :user="user.name"></Organization>
				</el-tab-pane>
			</el-tabs>
		</Page>
	</div>

</template>

<script setup lang='ts'>
import { computed, onMounted, ref } from 'vue';
import Page from '../../../../../../guigu_pm/guigu_pm/public/js/components/page/index.vue';
import Users from './components/Users.vue'
import FormDetail from './components/Detail.vue'
import Organization from './components/Organization.vue'
import type { User } from './type';

const user = ref<User>();
const activeName = ref<string>('info');
const userMeta = ref<locals.DocType>();
const memberMeta = ref<locals.DocType>();
const loading = ref<boolean>(true)

onMounted(async ()=>{
	userMeta.value = await getMeta('User')
	memberMeta.value = await getMeta('Tianjy Organization Member')
})
async function getMeta(doctype:string) {
	let local_meta = frappe.get_meta(doctype);
	if (local_meta) {
		return local_meta
	}
	await frappe.model.with_doctype(doctype);
	local_meta = frappe.get_meta(doctype);
	return local_meta || undefined;
}

function getPermission(meta:locals.DocType){
	if (!meta) {
		return { deletePermission: false, createPermission: false, writePermission:false };
	}
	const deletePermission = frappe.perm.has_perm(meta.name, 0, 'delete');
	const createPermission = frappe.perm.has_perm(meta.name, 0, 'create');
	const writePermission = frappe.perm.has_perm(meta.name, 0, 'write');
	return { deletePermission, createPermission, writePermission };
}
const userPermissions = computed(() => {
	return getPermission(userMeta.value)
});
const memberPermissions = computed(() => {
	return getPermission(memberMeta.value)
});
</script>

<style lang='less' scoped>
.user-tabs{
	height: 100%;
    display: flex;
    flex-direction: column;
}
.organization{
	height: 100%;
}
</style>
