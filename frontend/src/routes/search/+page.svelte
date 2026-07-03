<script lang="ts">
	import { onMount } from 'svelte';
	import { getTransactions, getCategories, ApiError } from '$lib/api';
	import type { Category, Transaction } from '$lib/types';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Card from '$lib/components/Card.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import Skeleton from '$lib/components/Skeleton.svelte';

	let transactions: Transaction[] = [];
	let categories: Category[] = [];
	let loading = true;
	let errorMessage = '';
	let query = '';
	let selectedCategory = '';
	let startDate = '';
	let endDate = '';

	onMount(async () => {
		try {
			[transactions, categories] = await Promise.all([getTransactions(500), getCategories()]);
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudieron cargar los movimientos.';
		} finally {
			loading = false;
		}
	});

	$: filteredResults = transactions.filter((tx) => {
		const matchTxt = tx.description.toLowerCase().includes(query.toLowerCase());
		const matchCat = selectedCategory === '' || tx.entries.some((e) => e.category_id === parseInt(selectedCategory));

		let matchDt = true;
		if (startDate || endDate) {
			const txTime = new Date(tx.date).getTime();
			const start = startDate ? new Date(startDate).getTime() : 0;
			const end = endDate ? new Date(endDate).getTime() : Infinity;
			matchDt = txTime >= start && txTime <= end;
		}
		return matchTxt && matchCat && matchDt;
	});
</script>

<main class="p-4 max-w-md mx-auto pt-6 pb-28">
	<PageHeader title="Buscar Gastos" />

	{#if errorMessage}
		<div class="p-3 mb-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-card text-xs font-bold text-center">
			{errorMessage}
		</div>
	{/if}

	<div class="bg-surface p-4 rounded-card border border-zinc-800 shadow-sm space-y-3 mb-4">
		<input
			type="text"
			placeholder="Filtrar por concepto..."
			bind:value={query}
			class="w-full p-2 bg-zinc-900 border border-zinc-800 rounded-xl text-xs text-white focus:outline-none placeholder-zinc-700"
		/>

		<select bind:value={selectedCategory} class="w-full p-2 bg-zinc-900 border border-zinc-800 rounded-xl text-xs text-white focus:outline-none">
			<option value="">Todas las categorías</option>
			{#each categories as cat}<option value={cat.id}>{cat.name}</option>{/each}
		</select>

		<div class="grid grid-cols-2 gap-2 pt-1">
			<div>
				<span class="text-[9px] font-bold text-zinc-500 block mb-0.5 uppercase">Desde</span>
				<input type="date" bind:value={startDate} class="w-full p-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs text-zinc-300" />
			</div>
			<div>
				<span class="text-[9px] font-bold text-zinc-500 block mb-0.5 uppercase">Hasta</span>
				<input type="date" bind:value={endDate} class="w-full p-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs text-zinc-300" />
			</div>
		</div>
	</div>

	<div class="space-y-2">
		<span class="text-[10px] font-bold text-zinc-500 uppercase block">Resultados ({filteredResults.length})</span>
		{#if loading}
			<Skeleton count={4} height="h-12" />
		{:else}
			{#each filteredResults as tx}
				<Card href="/transactions/{tx.id}" padding="p-3">
					<div class="flex justify-between items-center">
						<div>
							<span class="font-bold text-xs text-white block">{tx.description}</span>
							<span class="text-[9px] text-zinc-500 block">{new Date(tx.date).toLocaleDateString()}</span>
						</div>
						<span class="font-extrabold text-xs text-blue-400">
							${Math.abs(Number(tx.entries[0]?.amount ?? 0)).toLocaleString()}
						</span>
					</div>
				</Card>
			{:else}
				<EmptyState title="Sin resultados" subtitle="Probá otro filtro." />
			{/each}
		{/if}
	</div>
</main>
