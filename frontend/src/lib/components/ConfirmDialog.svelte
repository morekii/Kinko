<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import Button from './Button.svelte';

	export let open = false;
	export let title = '¿Confirmar acción?';
	export let message = '';
	export let confirmLabel = 'Confirmar';
	export let danger = true;

	const dispatch = createEventDispatcher();
</script>

{#if open}
	<div
		class="fixed inset-0 bg-black/70 z-[100] flex items-center justify-center p-4"
		role="presentation"
		on:click|self={() => dispatch('cancel')}
	>
		<div class="bg-surface border border-zinc-800 rounded-card p-5 max-w-xs w-full space-y-4 shadow-2xl">
			<div>
				<h3 class="font-bold text-white text-sm">{title}</h3>
				{#if message}
					<p class="text-xs text-zinc-500 mt-1">{message}</p>
				{/if}
			</div>
			<div class="flex gap-2">
				<Button variant="secondary" on:click={() => dispatch('cancel')}>Cancelar</Button>
				<Button variant={danger ? 'danger' : 'primary'} on:click={() => dispatch('confirm')}>
					{confirmLabel}
				</Button>
			</div>
		</div>
	</div>
{/if}
