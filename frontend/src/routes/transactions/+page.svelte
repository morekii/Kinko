<script lang="ts">
	import { onMount } from 'svelte';
	import { Search } from 'lucide-svelte';
	import { getTransactions, ApiError } from '$lib/api';
	import type { Transaction } from '$lib/types';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Card from '$lib/components/Card.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import Skeleton from '$lib/components/Skeleton.svelte';

	let transactions: Transaction[] = [];
	let loading = true;
	let errorMessage = '';

	onMount(async () => {
		try {
			transactions = await getTransactions(200);
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudieron cargar las transacciones.';
		} finally {
			loading = false;
		}
	});
</script>

<main class="p-4 max-w-md mx-auto pt-6 pb-28">
	<PageHeader title="Historial Completo">
		<svelte:fragment slot="actions">
			<a
				href="/search"
				class="text-xs font-bold text-zinc-400 bg-zinc-900 px-3 py-2 rounded-full hover:text-white transition-colors flex items-center gap-1"
			>
				<Search size={14} />
			</a>
		</svelte:fragment>
	</PageHeader>

	{#if errorMessage}
		<div class="p-3 mb-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-card text-xs font-bold text-center">
			{errorMessage}
		</div>
	{/if}

	<div class="space-y-2">
		{#if loading}
			<Skeleton count={6} height="h-14" />
		{:else}
			{#each transactions as tx}
				{@const amt = Number(tx.entries?.[0]?.amount ?? 0)}
				<Card href="/transactions/{tx.id}" padding="p-3">
					<div class="flex justify-between items-center">
						<div>
							<span class="font-bold text-xs text-white block">{tx.description}</span>
							<span class="text-[9px] text-zinc-500 block">{new Date(tx.date).toLocaleDateString()}</span>
						</div>
						<span class="font-extrabold text-xs {amt < 0 ? 'text-white' : 'text-emerald-400'}">
							{amt < 0 ? '-' : '+'}${Math.abs(amt).toLocaleString()}
						</span>
					</div>
				</Card>
			{:else}
				<EmptyState title="Sin movimientos" subtitle="Todavía no cargaste ninguna operación." />
			{/each}
		{/if}
	</div>
</main>
