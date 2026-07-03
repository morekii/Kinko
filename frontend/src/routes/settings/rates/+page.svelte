<script lang="ts">
	import { onMount } from 'svelte';
	import { Plus } from 'lucide-svelte';
	import { getRates, updateRates, ApiError } from '$lib/api';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Card from '$lib/components/Card.svelte';
	import Button from '$lib/components/Button.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import Skeleton from '$lib/components/Skeleton.svelte';

	interface RateRow {
		currency: string;
		rate: string;
	}

	let rows: RateRow[] = [];
	let loading = true;
	let saving = false;
	let successMessage = '';
	let errorMessage = '';

	let newCurrency = '';

	async function loadRates() {
		loading = true;
		errorMessage = '';
		try {
			const rates = await getRates();
			rows = rates.map((r) => ({ currency: r.currency, rate: String(r.rate_to_base) }));
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudieron cargar las cotizaciones.';
		} finally {
			loading = false;
		}
	}
	onMount(loadRates);

	function addRow() {
		const currency = newCurrency.trim().toUpperCase();
		if (!currency || rows.some((r) => r.currency === currency)) return;
		rows = [...rows, { currency, rate: '' }];
		newCurrency = '';
	}

	async function saveRates() {
		saving = true;
		errorMessage = '';
		successMessage = '';
		try {
			const payload: Record<string, number> = {};
			for (const row of rows) {
				if (row.rate !== '') payload[row.currency] = parseFloat(row.rate);
			}
			await updateRates(payload);
			successMessage = 'Cotizaciones actualizadas.';
			await loadRates();
			setTimeout(() => (successMessage = ''), 3000);
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudieron guardar las cotizaciones.';
		} finally {
			saving = false;
		}
	}
</script>

<main class="p-4 max-w-md mx-auto pt-6 pb-28">
	<PageHeader title="Cotizaciones Manuales" subtitle="1 unidad de cada moneda, expresada en tu moneda base (ARS)" />

	{#if successMessage}
		<div class="p-3 mb-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-card text-xs font-bold text-center">
			{successMessage}
		</div>
	{/if}
	{#if errorMessage}
		<div class="p-3 mb-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-card text-xs font-bold text-center">
			{errorMessage}
		</div>
	{/if}

	{#if loading}
		<Skeleton count={3} height="h-14" />
	{:else}
		<Card padding="p-4">
			<div class="space-y-3">
				{#each rows as row}
					<div class="flex items-center gap-3">
						<span class="w-24 shrink-0 text-xs font-bold text-blue-400 uppercase break-words">{row.currency}</span>
						<input
							type="number"
							step="any"
							placeholder="0.00"
							bind:value={row.rate}
							class="flex-1 p-2.5 bg-zinc-900 border border-zinc-800 rounded-xl text-sm text-white focus:outline-none"
						/>
					</div>
				{:else}
					<EmptyState title="Sin cotizaciones cargadas" subtitle="Agregá una moneda para empezar." />
				{/each}
			</div>
		</Card>

		<div class="flex gap-2 mt-3">
			<input
				type="text"
				placeholder="Nueva moneda (ej. USD)"
				bind:value={newCurrency}
				class="flex-1 p-3 bg-surface border border-zinc-800 rounded-xl text-sm text-white focus:outline-none placeholder-zinc-700"
			/>
			<Button variant="secondary" fullWidth={false} on:click={addRow}>
				<Plus size={16} />
			</Button>
		</div>

		<div class="mt-4">
			<Button on:click={saveRates} disabled={saving}>{saving ? 'Guardando...' : 'Guardar Cotizaciones'}</Button>
		</div>
	{/if}
</main>
