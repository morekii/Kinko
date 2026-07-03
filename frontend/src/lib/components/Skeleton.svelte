<script lang="ts">
	export let height = 'h-16';
	export let count = 1;
</script>

{#each Array(count) as _}
	<div class="w-full {height} bg-zinc-900 rounded-card animate-pulse border border-zinc-800 mb-3"></div>
{/each}
