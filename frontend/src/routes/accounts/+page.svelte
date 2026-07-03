<script lang="ts">
	import { onMount } from 'svelte';
	import { Plus, Star } from 'lucide-svelte';
	import { getAccounts, getBalances, createAccount, ApiError } from '$lib/api';
	import type { Account, AccountBalance } from '$lib/types';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Card from '$lib/components/Card.svelte';
	import Input from '$lib/components/Input.svelte';
	import Select from '$lib/components/Select.svelte';
	import Button from '$lib/components/Button.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import Skeleton from '$lib/components/Skeleton.svelte';
	import Badge from '$lib/components/Badge.svelte';

	let accounts: Account[] = [];
	let balances: AccountBalance[] = [];
	let loading = true;

	let name = '';
	let entity = '';
	let type = 'savings';
	let currency = 'ARS';
	let isDayToDay = true;
	let creating = false;
	let showAddForm = false;
	let errorMessage = '';

	async function loadAccounts() {
		loading = true;
		errorMessage = '';
		try {
			[accounts, balances] = await Promise.all([getAccounts(), getBalances()]);
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudieron cargar las cuentas.';
		} finally {
			loading = false;
		}
	}
	onMount(loadAccounts);

	$: if (type === 'investments') isDayToDay = false;

	function balanceFor(accountId: number) {
		return balances.find((b) => b.account_id === accountId)?.balance ?? null;
	}

	async function addAccount() {
		if (!name.trim() || !entity.trim()) return;
		creating = true;
		errorMessage = '';
		try {
			await createAccount({
				name: name.trim(),
				entity: entity.trim(),
				type: type as Account['type'],
				currency,
				is_day_to_day: isDayToDay,
				is_active: true
			});
			name = '';
			entity = '';
			type = 'savings';
			currency = 'ARS';
			isDayToDay = true;
			showAddForm = false;
			await loadAccounts();
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo crear la cuenta.';
		} finally {
			creating = false;
		}
	}
</script>

<main class="p-4 max-w-md mx-auto pt-6 pb-28">
	<PageHeader title="Cuentas" />

	{#if errorMessage}
		<div class="p-3 mb-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-card text-xs font-bold text-center">
			{errorMessage}
		</div>
	{/if}

	{#if !showAddForm}
		<button
			on:click={() => (showAddForm = true)}
			class="w-full bg-surface border border-dashed border-zinc-700 rounded-card p-6 mb-6 flex flex-col items-center justify-center text-zinc-500 hover:text-white hover:bg-zinc-800 transition-all cursor-pointer"
		>
			<Plus size={28} class="mb-2 text-blue-500" />
			<span class="text-sm font-bold tracking-wide">Crear Nueva Cuenta</span>
		</button>
	{:else}
		<form on:submit|preventDefault={addAccount} class="bg-surface border border-blue-500/30 p-5 rounded-card shadow-lg shadow-blue-900/10 mb-6 space-y-4">
			<div class="flex justify-between items-center mb-2">
				<span class="text-[10px] font-bold text-blue-400 uppercase tracking-wider">Nueva Cuenta</span>
				<button type="button" on:click={() => (showAddForm = false)} class="text-xs font-bold text-zinc-500 hover:text-white">Cancelar</button>
			</div>

			<div class="grid grid-cols-2 gap-3">
				<Input label="Nombre" placeholder="Ej. Ahorros" bind:value={name} required />
				<Input label="Entidad (Banco)" placeholder="Ej. Galicia" bind:value={entity} required />
			</div>

			<div class="grid grid-cols-2 gap-3">
				<Select label="Tipo" bind:value={type}>
					<option value="savings">Caja de Ahorro</option>
					<option value="checking">Cta. Corriente</option>
					<option value="credit_card">Tarjeta Crédito</option>
					<option value="cash">Efectivo</option>
					<option value="investments">Inversión / Cripto</option>
				</Select>
				<Select label="Moneda" bind:value={currency}>
					<option value="ARS">ARS</option>
					<option value="USD">USD</option>
					<option value="USDT">USDT</option>
					<option value="BTC">BTC</option>
				</Select>
			</div>

			<label class="flex items-center gap-2 pt-2 text-xs text-zinc-400 font-medium cursor-pointer border-t border-zinc-800">
				<input type="checkbox" bind:checked={isDayToDay} class="rounded bg-zinc-900 border-zinc-700 text-blue-500" />
				<span>Suma a liquidez "Día a Día"</span>
			</label>

			<Button type="submit" disabled={creating}>Crear Cuenta</Button>
		</form>
	{/if}

	<div class="space-y-3">
		<span class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block mb-2">Tus Cuentas Activas</span>
		{#if loading}
			<Skeleton count={3} />
		{:else}
			{#each accounts as acc}
				<Card href="/accounts/{acc.id}" padding="p-4">
					<div class="flex justify-between items-center">
						<div class="flex items-center gap-4">
							<div class="w-10 h-10 bg-zinc-900 rounded-xl flex items-center justify-center border border-zinc-800">
								<span class="text-blue-500 text-xs font-bold">{acc.currency}</span>
							</div>
							<div>
								<div class="flex items-center gap-1.5">
									<p class="font-bold text-sm text-white">{acc.entity}</p>
									{#if acc.is_main}<Star size={12} class="text-amber-400 fill-amber-400" />{/if}
								</div>
								<p class="text-[10px] text-zinc-500 font-medium">{acc.name} • {acc.type}</p>
							</div>
						</div>
						<div class="text-right">
							{#if balanceFor(acc.id) !== null}
								<p class="font-extrabold text-sm {Number(balanceFor(acc.id)) < 0 ? 'text-red-400' : 'text-emerald-400'}">
									{Number(balanceFor(acc.id)) < 0 ? '-' : ''}${Math.abs(Number(balanceFor(acc.id))).toLocaleString()}
								</p>
							{/if}
							{#if acc.is_day_to_day}
								<Badge>Liquidez</Badge>
							{/if}
						</div>
					</div>
				</Card>
			{:else}
				<EmptyState title="No hay cuentas" subtitle="Hacé clic arriba para cargar la primera." />
			{/each}
		{/if}
	</div>
</main>
