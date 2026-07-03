<script lang="ts">
	import { onMount } from 'svelte';
	import { Eye, EyeOff, Landmark, PiggyBank, TrendingUp } from 'lucide-svelte';
	import { getNetWorth, getBalances, getAccounts, getTransactions, getRates, ApiError } from '$lib/api';
	import type { Account, AccountBalance, Transaction, TotalBalance } from '$lib/types';
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
	let accountsFull: Account[] = [];
	let transactions: Transaction[] = [];
	let usdRate = 1;
	let loading = true;
	let showAmounts = true;
	let errorMessage = '';

	async function fetchData() {
		loading = true;
		errorMessage = '';
		try {
			const [net, balances, accs, tx, rates] = await Promise.all([
				getNetWorth(),
				getBalances(),
				getAccounts(),
				getTransactions(100),
				getRates()
			]);
			totalBalance = net;
			accounts = balances;
			accountsFull = accs;
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
			? `${val < 0 ? '-' : ''}${prefix}${Math.abs(val).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
			: '••••••';

	$: netWorthUsd = usdRate ? totalBalance.net_worth / usdRate : 0;

	$: mainAccount = accounts.find((a) => a.is_active && accountsFull.find((f) => f.id === a.account_id)?.is_main);

	$: savingsUsd =
		accounts
			.filter((a) => {
				if (!a.is_active || a.account_id === mainAccount?.account_id) return false;
				const type = accountsFull.find((f) => f.id === a.account_id)?.type;
				return type === 'savings' || type === 'investments';
			})
			.reduce((sum, a) => sum + Number(a.base_balance), 0) / (usdRate || 1);

	function displayBalance(acc: AccountBalance) {
		if (!showAmounts) return '••••••';
		if (acc.currency === 'ARS') return fmt(Number(acc.balance), true, '');
		const usdValue = usdRate ? Number(acc.base_balance) / usdRate : 0;
		return `${usdValue < 0 ? '-' : ''}U$S ${Math.abs(usdValue).toLocaleString('en-US', {
			minimumFractionDigits: 2,
			maximumFractionDigits: 2
		})}`;
	}

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
		<Card padding="p-5">
			<div class="flex items-center gap-2 mb-1">
				<div class="w-8 h-8 bg-emerald-500/20 rounded-lg flex items-center justify-center">
					<Landmark size={18} class="text-emerald-400" />
				</div>
				<p class="text-[10px] text-zinc-500 uppercase tracking-widest font-bold">Liquidez</p>
			</div>
			<p class="text-3xl font-extrabold tracking-tight mt-2 {totalBalance.day_to_day_available < 0 ? 'text-red-400' : 'text-white'}">
				{fmt(totalBalance.day_to_day_available, showAmounts)}
			</p>
		</Card>

		<div class="grid grid-cols-3 gap-3 pt-4">
			<div class="bg-surface border border-zinc-800 p-4 rounded-card flex flex-col justify-between shadow-lg">
				<div class="w-8 h-8 bg-violet-500/20 rounded-lg flex items-center justify-center mb-4">
					<TrendingUp size={18} class="text-violet-400" />
				</div>
				<div>
					<p class="text-[10px] text-zinc-500 font-bold uppercase tracking-wider truncate">Patrimonio (USD)</p>
					<p class="text-lg font-bold text-white mt-0.5">
						{showAmounts
							? `$ ${netWorthUsd.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
							: '••••••'}
					</p>
				</div>
			</div>

			<div class="bg-surface border border-zinc-800 p-4 rounded-card flex flex-col justify-between shadow-lg">
				<div class="w-8 h-8 bg-amber-500/20 rounded-lg flex items-center justify-center mb-4">
					<PiggyBank size={18} class="text-amber-400" />
				</div>
				<div>
					<p class="text-[10px] text-zinc-500 font-bold uppercase tracking-wider truncate">Ahorros (USD)</p>
					<p class="text-lg font-bold text-white mt-0.5">
						{showAmounts
							? `$ ${savingsUsd.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
							: '••••••'}
					</p>
				</div>
			</div>

			{#if mainAccount}
				<a
					href="/accounts/{mainAccount.account_id}"
					class="bg-surface border border-zinc-800 p-4 rounded-card flex flex-col justify-between hover:bg-zinc-800 transition-colors shadow-lg"
				>
					<div class="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4">
						<span class="text-blue-400 text-xs font-bold">{mainAccount.currency}</span>
					</div>
					<div>
						<p class="text-[10px] text-zinc-500 font-bold uppercase tracking-wider truncate">
							{mainAccount.account_name}
						</p>
						<p class="text-lg font-bold text-white mt-0.5">{displayBalance(mainAccount)}</p>
					</div>
				</a>
			{/if}
		</div>

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
