<template>
	<div v-if="hasTitle" class="title container">
		<ToggleBtn v-model:expand="showSider"></ToggleBtn>
		<slot name="title"></slot>
	</div>
	<div class="container guigu-container">
		<div class="tools" v-show="hasTools&&!smallMeta">

			<slot name="tools"></slot>
		</div>
		<div class="tools small-meta_tools" v-if="smallMeta">
			<ToggleBtn v-if="!hasTitle" v-model:expand="showSider">
			</ToggleBtn>
			<div v-else></div>
			<el-popover placement="bottom-start" :width="300" trigger="click">
				<template #reference>
					<el-icon size="20px">
						<MoreFilled />
					</el-icon>
				</template>
				<div class="popover-tools">
					<slot name="tools"></slot>
				</div>
			</el-popover>
		</div>
		<div :class="[mode === 'vertical'?'vertical':'horizon', 'main-container' ]"
			ref="container">
			<div :style="siderStyle"
				:class="['sider', {onlySider:hasSider&&!hasDetail&&!hasMain}]"
				v-show="hasSider&&!smallMeta&&showSider" ref="sider">
				<slot name="sider"></slot>
			</div>
			<div
				:class="[mode === 'vertical'?'vertical':'horizon', 'resizer-container' ]"
				v-show="hasSider&&(hasDetail||hasMain)&&!smallMeta&&showSider"
				ref="resizerContainer">
				<div
					class="resizer"
					title="侧边栏resizer"
					@pointerdown="dragLRController">
				</div>
			</div>
			<div
				:class="[rightMode === 'vertical'?'vertical':'horizon','right']"
				ref="rightContainer">
				<div :style="mainStyle" :class="['main', {noDetail:!hasDetail}]"
					v-show="hasMain"
					ref="main">
					<slot></slot>
				</div>
				<div
					:class="[rightMode === 'vertical'?'vertical':'horizon', 'resizer-container' ]"
					v-show="hasDetail&&hasMain"
					ref="mainResizerContainer">
					<div
						class="resizer"
						title="main resizer"
						@pointerdown="dragLRController">
					</div>
				</div>
				<div :style="detailStyle" class="detail" v-show="hasDetail">
					<slot name="detail"></slot>
				</div>
			</div>
		</div>
	</div>
	<el-drawer
		v-model="showDrawer"
		@close="closeDrawer"
		title=""
		direction="ltr"
		size="50%">
		<slot name="sider"></slot>
	</el-drawer>
</template>
<script lang="ts" setup>
import { useSlots, computed, ref, defineProps, CSSProperties, watch } from 'vue';
import {  Expand, MoreFilled} from '@element-plus/icons-vue';

import { useMetaQuery } from './useMetaQuery';
import ToggleBtn from './ToggleBtn.vue';
const smallMeta = useMetaQuery();
interface Props{
	mode?: 'horizon'| 'vertical'
	rightMode?:'horizon'| 'vertical'
	siderStyle?:CSSProperties
	mainStyle?:CSSProperties
	detailStyle?:CSSProperties
}
const props = defineProps<Props>();

const sider = ref<HTMLElement>();
const main = ref<HTMLElement>();
const container = ref<HTMLElement>();
const resizerContainer =ref<HTMLElement>();
const mainResizerContainer = ref<HTMLElement>();
const rightContainer = ref<HTMLElement>();

const hasTitle = computed(()=>Boolean(useSlots().title));
const hasTools = computed(()=>Boolean(useSlots().tools));
const hasSider = computed(()=>Boolean(useSlots().sider));
const hasMain = computed(()=>Boolean(useSlots().default));
const hasDetail = computed(()=>Boolean(useSlots().detail));

const height = computed(()=>hasTitle.value?`calc(100vh - 135px)`:`calc(100vh - 60px)`);
const showSider = ref<boolean>(true);

function dragLRController(dragEvent:PointerEvent){
	if (!dragEvent.target){ return; }
	dragEvent.target.setPointerCapture(true);
	dragEvent.stopPropagation();
	dragEvent.target.style.background = '#999';
	let resizerContainerElement:HTMLElement|undefined;
	let leftElement:HTMLElement|undefined;
	let containerElement:HTMLElement|undefined;
	const isSiderResize = dragEvent.target === resizerContainer.value?.firstChild;
	const mode = isSiderResize?'mode':'rightMode';
	if (isSiderResize){
		resizerContainerElement = resizerContainer.value;
		leftElement = sider.value;
		containerElement = container.value;

	} else {
		resizerContainerElement = mainResizerContainer.value;
		leftElement = main.value;
		containerElement = rightContainer.value;
	}

	let startPo = 0;
	let containerClientSize = 0;
	let oldSiderSize = 0;
	let resizerContainerElementSize = 0;
	if (props[mode]==='vertical'){
		startPo = dragEvent.clientY;
		dragEvent.target.top = dragEvent.target.offsetTop;
		containerClientSize = containerElement?.clientHeight||0;
		oldSiderSize = (resizerContainerElement?.offsetTop||0) - (containerElement?.offsetTop||0);
		resizerContainerElementSize = resizerContainerElement?.clientHeight||0;
	} else {
		startPo = dragEvent.clientX;
		dragEvent.target.left = dragEvent.target.offsetLeft;
		containerClientSize = containerElement?.clientWidth||0;
		oldSiderSize = (resizerContainerElement?.offsetLeft||0) - (containerElement?.offsetLeft||0);
		resizerContainerElementSize = resizerContainerElement?.clientWidth||0;
	}
	let newSiderSize = oldSiderSize;
	document.onpointermove = function(moveEvent:PointerEvent) {
		if (!dragEvent.target){ return; }
		let endPo = 0;
		if (props[mode]==='vertical'){
			endPo = moveEvent.clientY;
		} else {
			endPo = moveEvent.clientX;
		}
		let resizerDiff = endPo - startPo;
		// 左边区域最后的宽度 = 之前宽度 + 变化宽度
		newSiderSize = oldSiderSize + resizerDiff;
		// 右侧宽度 = 整体宽度 - 左侧宽度 - 拖拽按钮
		const mainSize = containerClientSize - newSiderSize - resizerContainerElementSize;
		let mainMaxSize = isSiderResize?250:150;
		if (isSiderResize&&props.mode==='vertical'&&props.rightMode==='vertical'&&main.value?.style?.height){
			const alreadyMainHeight = parseFloat(main.value.style.height.replaceAll('px', '')||'0');
			mainMaxSize = alreadyMainHeight + 150 + resizerContainerElementSize;
		} else if (isSiderResize&&props.mode!=='vertical'&&props.rightMode!=='vertical'&&main.value?.style?.width){
			const alreadyMainWidth = parseFloat(main.value.style.width.replaceAll('px', '')||'0');
			mainMaxSize = alreadyMainWidth + 150 + resizerContainerElementSize;
		}

		// 左侧最小50
		if (newSiderSize < 50) {
			newSiderSize = 50;
			resizerDiff = newSiderSize - oldSiderSize;
		}
		// 右侧最小150
		if ( mainSize < mainMaxSize ) {
			newSiderSize = containerClientSize - mainMaxSize - resizerContainerElementSize;
			resizerDiff = newSiderSize - oldSiderSize;
		}

		// 设置resizer的位置
		if (props[mode]==='vertical'){
			dragEvent.target.style.top = `${resizerDiff}px`;
		} else {
			dragEvent.target.style.left = `${resizerDiff}px`;
		}
	};
	document.onpointerup = function(evt:PointerEvent) {
		if (!dragEvent.target){ return; }
		//颜色恢复
		dragEvent.target.style.background = '#d9d9d9';
		dragEvent.target.style.left = 'auto';
		dragEvent.target.style.top = 'auto';
		if (!leftElement){ return; }
		if (props[mode]==='vertical'){
			leftElement.style.height = `${newSiderSize}px`;
		} else {
			leftElement.style.width = `${newSiderSize}px`;
		}
		document.onpointermove = null;
		document.onpointerup = null;
	};

}
watch(()=>smallMeta.value, ()=>{
	if (smallMeta.value){
		showSider.value=false;
	}
}, {immediate:true});
const showDrawer = computed(()=>showSider.value&&smallMeta.value);
function closeDrawer(){
	showSider.value = false;
}
function toggleSider(){
	showSider.value = !showSider.value;
}
</script>
<style lang="less" scoped>
.title {
	height: 75px;
	height: 75px;
	display: flex;
	align-items: center;
	line-height: 75px;
}

.guigu-container {
	// height: calc(100vh - 60px);
	height: v-bind(height);
	display: flex;
	flex-direction: column;
	background-color: #fff;

	.main-container {
		flex: 1;
		display: flex;
		overflow: hidden;

		.sider {
			min-width: 50px;
			min-height: 50px;
		}

		&.horizon {
			flex-direction: row;

			.sider {
				width: 300px;

				&.onlySider {
					width: 100%
				}
			}
		}

		&.vertical {
			flex-direction: column;

			.sider {
				height: 300px;

				&.onlySider {
					height: 100%
				}
			}
		}

		.resizer-container {
			position: relative;
			border: 0;

			.resizer {
				position: absolute;
				z-index: 1;
				background-color: #d9d9d9;
				opacity: 0.5;
			}

			&.horizon {
				padding: 0 4px;
				width: 12px;
				height: 100%;

				.resizer {
					width: 2px;
					height: 100%;
					cursor: col-resize;
				}
			}

			&.vertical {
				padding: 4px 0;
				width: 100%;
				height: 12px;

				.resizer {
					height: 2px;
					width: 100%;
					cursor: row-resize;
				}
			}
		}


		.right {
			display: flex;
			flex: 1;
			overflow: auto;

			&.horizon {
				flex-direction: row;

				.main {
					width: 50%;

					&.noDetail {
						width: 100%;
					}
				}

				.detail {
					flex: 1;
					min-width: 150px;
				}
			}

			&.vertical {
				flex-direction: column;

				.main {
					height: 50%;

					&.noDetail {
						height: 100%;
					}
				}

				.detail {
					flex: 1;
					min-height: 150px;
				}
			}
		}

	}
}

.tools {
	padding: 8px 0;
}

.small-meta_tools {
	display: flex;
	justify-content: space-between;
}
</style>
