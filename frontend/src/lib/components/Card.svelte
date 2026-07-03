<script lang="ts">
	export let dashed = false;
	export let padding = 'p-4';
	export let href: string | undefined = undefined;

	$: classes = `bg-surface border ${
		dashed ? 'border-dashed border-zinc-700' : 'border-zinc-800'
	} rounded-card shadow-lg ${padding} ${href ? 'block hover:border-zinc-600 transition-colors' : ''}`;
</script>

{#if href}
	<a {href} on:click class={classes}>
		<slot />
	</a>
{:else}
	<div class={classes}>
		<slot />
	</div>
{/if}
