<script>
	import '../app.css';
	import BottomNav from '$lib/components/BottomNav.svelte';
</script>

<div class="bg-black text-white min-h-screen font-sans pb-24 selection:bg-blue-500/30">
	<slot />

	<BottomNav />
</div>
