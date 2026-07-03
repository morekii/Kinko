<script lang="ts">
	import { onMount } from 'svelte';
	import { Eye, EyeOff, Landmark, Plus } from 'lucide-svelte';
	import { getNetWorth, getBalances, getTransactions, getRates, ApiError } from '$lib/api';
	import type { AccountBalance, Transaction, TotalBalance } from '$lib/types';
	import Card from '$lib/components/Card.svelte';
	import Skeleton from '$lib/components/Skeleton.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import StatTile from '$lib/components/StatTile.svelte';

	let totalBalance: TotalBalance = {
		day_to_day_available: 0,
		total_assets: 0,
		total_liabilities: 0,
		net_worth: 0
	};
	let accounts: AccountBalance[] = [];
	let transactions: Transaction[] = [];
	let usdRate = 1;
	let loading = true;
	let showAmounts = true;
	let errorMessage = '';

	async function fetchData() {
		loading = true;
		errorMessage = '';
		try {
			const [net, balances, tx, rates] = await Promise.all([
				getNetWorth(),
				getBalances(),
				getTransactions(100),
				getRates()
			]);
			totalBalance = net;
			accounts = balances;
			transactions = tx;
			const usd = rates.find((r) => r.currency === 'USD');
			usdRate = usd ? Number(usd.rate_to_base) : 1;
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo conectar con el backend.';
		} finally {
			loading = false;
		}
	}

	onMount(fetchData);

	const fmt = (val: number, show: boolean, prefix = '$') =>
		show
			? `${prefix}${val.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
			: '••••••';

	$: netWorthUsd = usdRate ? totalBalance.net_worth / usdRate : 0;

	const now = new Date();
	$: monthTx = transactions.filter((tx) => {
		const d = new Date(tx.date);
		return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth();
	});
	$: monthExpenses = monthTx.reduce(
		(sum, tx) =>
			sum +
			tx.entries
				.filter((e) => e.category_id && Number(e.base_amount) > 0)
				.reduce((s, e) => s + Number(e.base_amount), 0),
		0
	);
	$: monthIncome = monthTx.reduce(
		(sum, tx) =>
			sum +
			tx.entries
				.filter((e) => e.category_id && Number(e.base_amount) < 0)
				.reduce((s, e) => s + Math.abs(Number(e.base_amount)), 0),
		0
	);
</script>

<main class="p-4 max-w-md mx-auto pt-6">
	<header class="flex justify-between items-center mb-6">
		<h1 class="text-3xl font-extrabold text-white tracking-tight">Inicio</h1>
		<button
			type="button"
			on:click={() => (showAmounts = !showAmounts)}
			class="p-2 bg-zinc-900 rounded-full text-zinc-400 hover:text-white transition-colors"
		>
			{#if showAmounts}<Eye size={20} />{:else}<EyeOff size={20} />{/if}
		</button>
	</header>

	{#if errorMessage}
		<div class="p-3 mb-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-card text-xs font-bold text-center">
			{errorMessage}
		</div>
	{/if}

	{#if loading}
		<Skeleton height="h-32" />
		<Skeleton height="h-40" />
		<Skeleton height="h-48" />
	{:else}
		<div class="flex overflow-x-auto pb-4 -mx-4 px-4 gap-3 snap-x no-scrollbar">
			<div
				class="min-w-[150px] bg-surface border border-zinc-800 p-4 rounded-card snap-start shrink-0 flex flex-col justify-between shadow-lg"
			>
				<div class="w-8 h-8 bg-emerald-500/20 rounded-lg flex items-center justify-center mb-4">
					<Landmark size={18} class="text-emerald-400" />
				</div>
				<div>
					<p class="text-[10px] text-zinc-500 font-bold uppercase tracking-wider">Efectivo día a día</p>
					<p class="text-lg font-bold text-white mt-0.5">
						{fmt(totalBalance.day_to_day_available, showAmounts)}
					</p>
				</div>
			</div>

			{#each accounts.filter((a) => a.is_active) as acc}
				<a
					href="/accounts/{acc.account_id}"
					class="min-w-[140px] bg-surface border border-zinc-800 p-4 rounded-card snap-start shrink-0 flex flex-col justify-between hover:bg-zinc-800 transition-colors shadow-lg"
				>
					<div class="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4">
						<span class="text-blue-400 text-xs font-bold">{acc.currency}</span>
					</div>
					<div>
						<p class="text-[10px] text-zinc-500 font-bold uppercase tracking-wider truncate">
							{acc.account_name}
						</p>
						<p class="text-lg font-bold text-white mt-0.5">{fmt(Number(acc.balance), showAmounts, '')}</p>
					</div>
				</a>
			{/each}

			<a
				href="/accounts"
				class="min-w-[130px] bg-zinc-900/50 border border-dashed border-zinc-700 p-4 rounded-card snap-start shrink-0 flex flex-col items-center justify-center hover:bg-zinc-800 transition-colors text-zinc-500 hover:text-zinc-300"
			>
				<div class="w-10 h-10 bg-accent rounded-full flex items-center justify-center mb-2 text-white">
					<Plus size={20} strokeWidth={2.5} />
				</div>
				<span class="text-xs font-semibold">Agregar cuenta</span>
			</a>
		</div>

		<Card padding="p-5" >
			<div class="mb-1">
				<p class="text-[10px] text-zinc-500 uppercase tracking-widest mb-1">Patrimonio global (USD)</p>
				<p class="text-3xl font-extrabold text-white tracking-tight">
					{showAmounts
						? `$ ${netWorthUsd.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
						: '••••••'}
				</p>
			</div>
		</Card>

		<div class="flex gap-3 mt-4">
			<StatTile label="Ingresos del mes" value={fmt(monthIncome, showAmounts)} tone="positive" />
			<StatTile label="Gastos del mes" value={fmt(monthExpenses, showAmounts)} tone="negative" />
		</div>

		<div class="bg-surface border border-zinc-800 rounded-card p-5 mt-4 mb-6 shadow-lg">
			<h3 class="text-[13px] font-bold text-white tracking-wide mb-4">Últimos movimientos</h3>

			<div class="space-y-4">
				{#each transactions.slice(0, 4) as tx}
					{@const amt = Number(tx.entries?.[0]?.amount ?? 0)}
					<a href="/transactions/{tx.id}" class="flex justify-between items-center group">
						<div class="flex items-center gap-3">
							<div
								class="w-10 h-10 rounded-full flex items-center justify-center {amt < 0
									? 'bg-zinc-800 text-zinc-300'
									: 'bg-emerald-500/15 text-emerald-400'}"
							>
								<Landmark size={18} />
							</div>
							<div>
								<p
									class="font-bold text-sm text-zinc-100 group-hover:text-blue-400 transition-colors truncate w-36"
								>
									{tx.description}
								</p>
								<p class="text-[10px] text-zinc-500 font-medium">{new Date(tx.date).toLocaleDateString()}</p>
							</div>
						</div>
						<div class="text-right">
							<p class="font-bold text-[13px] {amt < 0 ? 'text-white' : 'text-emerald-400'}">
								{showAmounts ? `${amt < 0 ? '-' : '+'}$${Math.abs(amt).toLocaleString()}` : '••••'}
							</p>
						</div>
					</a>
				{:else}
					<EmptyState title="Sin movimientos" subtitle="Cargá tu primera operación desde el botón +." />
				{/each}
			</div>
		</div>
	{/if}
</main>

<style>
	.no-scrollbar::-webkit-scrollbar {
		display: none;
	}
	.no-scrollbar {
		-ms-overflow-style: none;
		scrollbar-width: none;
	}
</style>
