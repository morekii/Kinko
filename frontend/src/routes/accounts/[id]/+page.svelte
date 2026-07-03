<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { Star } from 'lucide-svelte';
	import {
		getAccounts,
		getBalances,
		getTransactions,
		updateAccount,
		deleteAccount,
		ApiError
	} from '$lib/api';
	import type { Account, Transaction } from '$lib/types';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Card from '$lib/components/Card.svelte';
	import Input from '$lib/components/Input.svelte';
	import Select from '$lib/components/Select.svelte';
	import Button from '$lib/components/Button.svelte';
	import Badge from '$lib/components/Badge.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';

	const accountId = parseInt($page.params.id as string);

	let account: Account | null = null;
	let allAccounts: Account[] = [];
	let balance: number | null = null;
	let transactions: Transaction[] = [];
	let loading = true;
	let errorMessage = '';

	let isEditing = false;
	let editName = '';
	let editEntity = '';
	let editCurrency = 'ARS';
	let editIsDayToDay = true;
	let editIsMain = false;
	let editReserveAccountId: any = null;
	let saving = false;
	let confirmDeleteOpen = false;

	async function loadAccountHub() {
		loading = true;
		errorMessage = '';
		try {
			const [accs, balances, tx] = await Promise.all([
				getAccounts(),
				getBalances(),
				getTransactions(300)
			]);
			allAccounts = accs;
			account = accs.find((a) => a.id === accountId) ?? null;
			balance = balances.find((b) => b.account_id === accountId)?.balance ?? null;
			transactions = tx.filter((t) => t.entries.some((e) => e.account_id === accountId));
			if (account) {
				editName = account.name;
				editEntity = account.entity;
				editCurrency = account.currency;
				editIsDayToDay = account.is_day_to_day;
				editIsMain = account.is_main;
				editReserveAccountId = account.reserve_account_id;
			}
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo cargar la cuenta.';
		} finally {
			loading = false;
		}
	}
	onMount(loadAccountHub);

	function entryFor(tx: Transaction) {
		return tx.entries.find((e) => e.account_id === accountId);
	}

	async function saveChanges() {
		saving = true;
		errorMessage = '';
		try {
			await updateAccount(accountId, {
				name: editName,
				entity: editEntity,
				currency: editCurrency,
				is_day_to_day: editIsDayToDay,
				is_main: editIsMain,
				reserve_account_id: editReserveAccountId ? Number(editReserveAccountId) : null
			});
			isEditing = false;
			await loadAccountHub();
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo guardar la cuenta.';
		} finally {
			saving = false;
		}
	}

	async function confirmDelete() {
		confirmDeleteOpen = false;
		errorMessage = '';
		try {
			await deleteAccount(accountId);
			history.back();
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo desactivar la cuenta.';
		}
	}
</script>

<main class="p-4 max-w-md mx-auto pt-6 pb-28">
	<PageHeader title="Detalle de Cuenta" />

	{#if errorMessage}
		<div class="p-3 mb-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-card text-xs font-bold text-center">
			{errorMessage}
		</div>
	{/if}

	{#if !loading && account}
		<Card padding="p-5">
			<div class="flex justify-between items-center mb-3">
				<span class="text-[10px] text-zinc-500 font-bold uppercase">Configuración</span>
				<button type="button" on:click={() => (isEditing = !isEditing)} class="text-xs text-blue-400 font-semibold">
					{isEditing ? 'Cancelar' : 'Editar'}
				</button>
			</div>

			{#if isEditing}
				<div class="space-y-3">
					<div class="grid grid-cols-2 gap-3">
						<Input label="Nombre" bind:value={editName} />
						<Input label="Entidad" bind:value={editEntity} />
					</div>
					<Select label="Moneda" bind:value={editCurrency}>
						<option value="ARS">ARS</option>
						<option value="USD">USD</option>
						<option value="USDT">USDT</option>
						<option value="BTC">BTC</option>
					</Select>

					{#if account.type === 'credit_card'}
						<Select label="Cuenta de reserva (sobre para el resumen)" bind:value={editReserveAccountId}>
							<option value={null}>Sin configurar</option>
							{#each allAccounts.filter((a) => a.id !== accountId && a.type !== 'credit_card') as acc}
								<option value={acc.id}>{acc.entity} - {acc.name}</option>
							{/each}
						</Select>
					{/if}

					<label class="flex items-center gap-2 text-xs text-zinc-400 font-medium cursor-pointer">
						<input type="checkbox" bind:checked={editIsDayToDay} class="rounded bg-zinc-900 border-zinc-700 text-blue-500" />
						<span>Suma a liquidez "Día a Día"</span>
					</label>
					<label class="flex items-center gap-2 text-xs text-zinc-400 font-medium cursor-pointer">
						<input type="checkbox" bind:checked={editIsMain} class="rounded bg-zinc-900 border-zinc-700 text-amber-500" />
						<span>Marcar como Cuenta Principal</span>
					</label>

					<Button on:click={saveChanges} disabled={saving} variant="primary">Guardar Cambios</Button>
				</div>
			{:else}
				<div class="flex items-center gap-2">
					<h2 class="text-lg font-bold text-white">{account.entity} - {account.name}</h2>
					{#if account.is_main}<Star size={16} class="text-amber-400 fill-amber-400" />{/if}
				</div>
				<p class="text-[10px] text-zinc-500 mt-1 uppercase tracking-wide">{account.type} • {account.currency}</p>
				{#if balance !== null}
					<p class="text-2xl font-extrabold mt-3 {Number(balance) < 0 ? 'text-red-400' : 'text-emerald-400'}">
						{Number(balance) < 0 ? '-' : ''}${Math.abs(Number(balance)).toLocaleString()}
					</p>
				{/if}
				<div class="flex gap-2 mt-3">
					{#if account.is_day_to_day}<Badge>Liquidez</Badge>{/if}
					{#if account.reserve_account_id}<Badge color="blue">Con reserva configurada</Badge>{/if}
				</div>
			{/if}

			<Button variant="danger" on:click={() => (confirmDeleteOpen = true)} fullWidth>
				Desactivar Cuenta
			</Button>
		</Card>

		<div class="space-y-2 mt-6">
			<span class="text-[10px] text-zinc-500 font-bold uppercase block">Movimientos</span>
			{#each transactions as tx}
				{@const entry = entryFor(tx)}
				<Card href="/transactions/{tx.id}" padding="p-3">
					<div class="flex justify-between items-center">
						<div>
							<span class="font-bold text-xs text-white block">{tx.description}</span>
							<span class="text-[9px] text-zinc-500 block">{new Date(tx.date).toLocaleDateString()}</span>
						</div>
						<span class="font-extrabold text-xs {Number(entry?.amount) < 0 ? 'text-white' : 'text-emerald-400'}">
							{Number(entry?.amount) < 0 ? '-' : '+'}${Math.abs(Number(entry?.amount ?? 0)).toLocaleString()}
						</span>
					</div>
				</Card>
			{:else}
				<EmptyState title="Sin movimientos" subtitle="Todavía no hay operaciones en esta cuenta." />
			{/each}
		</div>
	{/if}
</main>

<ConfirmDialog
	open={confirmDeleteOpen}
	title="¿Desactivar esta cuenta?"
	message="Vas a poder reactivarla más adelante; el historial de movimientos se conserva."
	confirmLabel="Desactivar"
	on:confirm={confirmDelete}
	on:cancel={() => (confirmDeleteOpen = false)}
/>
