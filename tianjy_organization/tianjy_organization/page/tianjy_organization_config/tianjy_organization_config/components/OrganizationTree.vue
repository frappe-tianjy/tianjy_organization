
<template>
	<div class="sider-container">
		<div>
		<el-button type="primary" @click="createOrganization">新建组织</el-button>
	</div>
	<div class="tree-container">
		<el-tree 
			v-if="organizationTree.length>0"
			:data="organizationTree"  
			@node-click="handleNodeClick" 
			default-expand-all
			highlight-current
			node-key="name"
			:current-node-key="currentNodeKey"
			:expand-on-click-node="false"
			draggable
			@node-drop="handleDrop"
			:allow-drop="allowDrop"
		>
			<template #default="{ node, data }">
				<TreeItem 
					:node="node"
					@reload="getOrganizations"
				></TreeItem>
			</template>
		</el-tree>	
	</div>
	</div>

</template>

<script setup lang='ts'>
import { ref, onMounted, computed, toRaw} from 'vue';
import type { Organization, OrganizationType, Permissions } from '../type';
import { list2Tree } from '../helper';
import type {
  AllowDropType,
  NodeDropType,
} from 'element-plus/es/components/tree/src/tree.type'
import type { DragEvents } from 'element-plus/es/components/tree/src/model/useDragNode'
import type Node from 'element-plus/es/components/tree/src/model/node'
import TreeItem from './TreeItem.vue'
import { ElMessage } from 'element-plus';
interface Props{
	modelValue?:Organization
	permissions: Permissions
}
const props = defineProps<Props>();
interface Emit{
	(e:'update:modelValue', organization:any ):void
}
const emit = defineEmits<Emit>();
const organizationList = ref<Organization[]>([]);
const currentNodeKey = ref<string>('');

onMounted(()=>{
	getOrganizations();
})
async function getOrganizations(){
	const res = await frappe.call<{ message: Organization[] }>({
		method: 'tianjy_organization.tianjy_organization.page.tianjy_organization_config.tianjy_organization_config.get_organizations',
	});
	organizationList.value = res?.message||[]
	if(!currentNodeKey.value){
		currentNodeKey.value =  organizationList.value[0]?.name
		emit('update:modelValue', organizationList.value[0])
	}
}

const organizationTree = computed(()=>{
	for(const org of organizationList.value){
		org.permissions = props.permissions
	}
	return list2Tree(toRaw(organizationList.value), 'parent_organization')
})

function handleNodeClick(data:Organization){
	emit('update:modelValue', data)
}

function createOrganization(){
	const newDoc = frappe.model.make_new_doc_and_get_name('Tianjy Organization');
	frappe.set_route(['form', 'Tianjy Organization', newDoc]);
}
async function handleDrop( 
	draggingNode: Node,
  	dropNode: Node,
  	dropType: NodeDropType,
  	ev: DragEvents
){
	const before = dropType==='inner'?false:dropType ==='before'
	const children = dropType==='inner'
	await frappe.call('guigu.tree.tree_sort', {
				doctype: 'Tianjy Organization',
				target:dropNode.data.name, 
				docs:[draggingNode.data.name], 
				before,
				children,
			});
	getOrganizations()
}

function allowDrop(
	draggingNode: Node,
  	dropNode: Node,
  	dropType: AllowDropType,
){
	switch(dropType){
		case 'next':
		case 'prev': return before(draggingNode, dropNode);
		case 'inner': return inner(draggingNode, dropNode);
		default: return true
	}
}
function inner(
	draggingNode: Node,
  	dropNode: Node,
){
	// 放到其他节点内
	// 判断能不能作为这个节点的子节点
	if(!dropNode.data.child_type_list.some(type=>type.name===draggingNode.data.type)){
		return false;
	}
	return true
}
function before(
	draggingNode: Node,
  	dropNode: Node,
){
	if(dropNode.parent.level===0&&draggingNode.data.type_doc.root_only!==1){
		console.log(dropNode.parent.level, draggingNode.data.type_doc.root_only, 'false')
		return false;
	}
	// 不是放到根节点，判断能不能作为其他节点的子级
	if(dropNode.parent.level!==0&&!dropNode.parent.data.child_type_list.some(type=>type.name===draggingNode.data.type)){
		console.log(dropNode.parent.level, 'false')
		return false;
	}
	return true
}
frappe.socketio.doctype_subscribe('Tianjy Organization');
frappe.realtime.on('list_update', p => {
	if (p.doctype !== 'Tianjy Organization') { return; }
	getOrganizations();
});

</script>

<style lang='less' scoped>
.sider-container{
	display: flex;
	flex-direction: column;
	height: 100%;
	padding-top: 8px;
	.tree-container{
		overflow-y: auto;
	}
}
</style>
