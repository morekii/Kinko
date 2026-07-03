<script lang="ts">
	import { onMount } from 'svelte';
	import { Plus } from 'lucide-svelte';
	import { getRates, updateRates, refreshRates, ApiError } from '$lib/api';
	import { RefreshCw } from 'lucide-svelte';
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
	let refreshing = false;
	let successMessage = '';
	let errorMessage = '';

	let newCurrency = '';

	$: usdRate = Number(rows.find((r) => r.currency === 'USD')?.rate) || 0;

	function btcUsdDisplay(row: RateRow) {
		if (!usdRate) return row.rate;
		return (Number(row.rate || 0) / usdRate).toFixed(2);
	}

	function onBtcUsdInput(row: RateRow, value: string) {
		const usdValue = parseFloat(value || '0');
		row.rate = usdRate ? String(usdValue * usdRate) : value;
	}

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

	async function refreshFromApis() {
		refreshing = true;
		errorMessage = '';
		successMessage = '';
		try {
			await refreshRates();
			successMessage = 'Oficial, Tarjeta, Cripto y BTC actualizados desde las APIs.';
			await loadRates();
			setTimeout(() => (successMessage = ''), 3000);
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo conectar con las APIs externas.';
		} finally {
			refreshing = false;
		}
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
		<Button variant="secondary" on:click={refreshFromApis} disabled={refreshing}>
			<span class="flex items-center justify-center gap-2">
				<RefreshCw size={14} class={refreshing ? 'animate-spin' : ''} />
				{refreshing ? 'Actualizando...' : 'Actualizar Oficial / Tarjeta / Cripto / BTC'}
			</span>
		</Button>
		<p class="text-[9px] text-zinc-500 mt-2 mb-4 text-center">
			Trae Oficial, Tarjeta y Cripto de dolarapi.com, y BTC de Coinbase (se muestra y edita en USD
			abajo, aunque por dentro se guarda convertido a ARS para poder usarlo en tus cuentas y
			transferencias). También corre solo, todos los días a las 00:00.
		</p>

		<Card padding="p-4">
			<div class="space-y-3">
				{#each rows as row}
					<div class="flex items-center gap-3">
						<span class="w-24 shrink-0 text-xs font-bold text-blue-400 uppercase break-words">{row.currency}</span>
						{#if row.currency === 'BTC'}
							<input
								type="number"
								step="any"
								placeholder="0.00"
								value={btcUsdDisplay(row)}
								on:input={(e) => onBtcUsdInput(row, e.currentTarget.value)}
								class="flex-1 p-2.5 bg-zinc-900 border border-zinc-800 rounded-xl text-sm text-white focus:outline-none"
							/>
							<span class="text-[9px] font-bold text-zinc-500 shrink-0">USD</span>
						{:else}
							<input
								type="number"
								step="any"
								placeholder="0.00"
								bind:value={row.rate}
								class="flex-1 p-2.5 bg-zinc-900 border border-zinc-800 rounded-xl text-sm text-white focus:outline-none"
							/>
						{/if}
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
