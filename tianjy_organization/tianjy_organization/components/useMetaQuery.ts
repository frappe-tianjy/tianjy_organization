import { ref, onMounted, onUnmounted, Ref } from 'vue';

export function useMetaQuery(): Ref<boolean>{
	const smallMeta = ref<boolean>('ontouchstart' in document.documentElement);
	let mQuery:MediaQueryList;
	function mediaChange(){
		if (mQuery.matches){
			smallMeta.value=true;
		} else {
			smallMeta.value=false;
		}
	}
	onMounted(()=>{
		mQuery = window.matchMedia('(max-width: 640px)');
		if (mQuery.matches){
			smallMeta.value=true;
		} else {
			smallMeta.value=false;
		}
		mQuery.addEventListener('change', mediaChange);
	});
	onUnmounted(()=>{
		mQuery.removeEventListener('change', mediaChange);
	});
	return smallMeta;
}
