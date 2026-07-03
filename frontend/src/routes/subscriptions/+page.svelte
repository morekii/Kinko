<script lang="ts">
	import { onMount } from 'svelte';
	import { Plus } from 'lucide-svelte';
	import { getSubscriptions, getCategories, getAccounts, createSubscription, deleteSubscription, ApiError } from '$lib/api';
	import type { Account, Category, Subscription } from '$lib/types';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Card from '$lib/components/Card.svelte';
	import Input from '$lib/components/Input.svelte';
	import Select from '$lib/components/Select.svelte';
	import Button from '$lib/components/Button.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import Skeleton from '$lib/components/Skeleton.svelte';
	import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';

	let subscriptions: Subscription[] = [];
	let categories: Category[] = [];
	let accounts: Account[] = [];
	let loading = true;

	let showAddForm = false;
	let description = '';
	let amount: number | string = '';
	let currency = 'ARS';
	let chargeDay = 1;
	let suggestedAccountId: any = null;
	let categoryId: any = null;
	let creating = false;

	let confirmDeleteId: number | null = null;
	let errorMessage = '';

	async function loadHub() {
		loading = true;
		errorMessage = '';
		try {
			[subscriptions, categories, accounts] = await Promise.all([getSubscriptions(), getCategories(), getAccounts()]);
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudieron cargar las suscripciones.';
		} finally {
			loading = false;
		}
	}
	onMount(loadHub);

	async function addSubscription() {
		if (!description.trim() || !amount) return;
		creating = true;
		errorMessage = '';
		try {
			await createSubscription({
				description: description.trim(),
				amount: parseFloat(amount as string),
				currency,
				charge_day: chargeDay,
				suggested_account_id: suggestedAccountId,
				category_id: categoryId,
				is_active: true
			});
			description = '';
			amount = '';
			currency = 'ARS';
			chargeDay = 1;
			suggestedAccountId = null;
			categoryId = null;
			showAddForm = false;
			await loadHub();
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo crear la suscripción.';
		} finally {
			creating = false;
		}
	}

	async function confirmDelete() {
		if (confirmDeleteId === null) return;
		errorMessage = '';
		try {
			await deleteSubscription(confirmDeleteId);
			confirmDeleteId = null;
			await loadHub();
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo dar de baja la suscripción.';
			confirmDeleteId = null;
		}
	}
</script>

<main class="p-4 max-w-md mx-auto pt-6 pb-28">
	<PageHeader title="Servicios" />

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
			<span class="text-sm font-bold tracking-wide">Nueva Suscripción</span>
		</button>
	{:else}
		<form on:submit|preventDefault={addSubscription} class="bg-surface border border-blue-500/30 p-5 rounded-card shadow-lg shadow-blue-900/10 mb-6 space-y-4">
			<div class="flex justify-between items-center mb-2">
				<span class="text-[10px] font-bold text-blue-400 uppercase tracking-wider">Nuevo Cargo Automático</span>
				<button type="button" on:click={() => (showAddForm = false)} class="text-xs font-bold text-zinc-500 hover:text-white">Cancelar</button>
			</div>

			<div class="grid grid-cols-3 gap-3">
				<div class="col-span-2"><Input label="Servicio" placeholder="Ej. Netflix" bind:value={description} required /></div>
				<Input label="Día Cobro" type="number" min={1} max={31} bind:value={chargeDay} />
			</div>

			<div class="grid grid-cols-3 gap-3">
				<div class="col-span-2"><Input label="Costo Fijo" type="number" step="any" placeholder="0.00" bind:value={amount} required /></div>
				<Select label="Moneda" bind:value={currency}>
					<option value="ARS">ARS</option>
					<option value="USD">USD</option>
				</Select>
			</div>

			<div class="grid grid-cols-2 gap-3 pt-2 border-t border-zinc-800">
				<Select label="Debitar de" bind:value={suggestedAccountId} required>
					<option value={null}>Selec. Cuenta</option>
					{#each accounts as acc}<option value={acc.id}>💳 {acc.name}</option>{/each}
				</Select>
				<Select label="Categoría" bind:value={categoryId} required>
					<option value={null}>Selec. Rubro</option>
					{#each categories as cat}<option value={cat.id}>🏷️ {cat.name}</option>{/each}
				</Select>
			</div>

			<Button type="submit" disabled={creating}>Programar Cargo</Button>
		</form>
	{/if}

	<div class="space-y-3">
		<span class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block mb-2">Próximos Vencimientos</span>
		{#if loading}
			<Skeleton count={3} />
		{:else}
			{#each subscriptions as sub}
				<Card padding="p-4">
					<div class="flex justify-between items-center">
						<div class="flex items-center gap-4">
							<div class="w-12 h-12 bg-zinc-900 rounded-2xl flex flex-col items-center justify-center border border-zinc-800">
								<span class="text-[9px] text-zinc-500 font-bold uppercase">DÍA</span>
								<span class="text-sm text-blue-400 font-extrabold">{sub.charge_day}</span>
							</div>
							<div>
								<p class="font-bold text-sm text-white">{sub.description}</p>
								<p class="text-[10px] text-zinc-500 font-medium">
									Categoría: {categories.find((c) => c.id === sub.category_id)?.name ?? 'N/A'}
								</p>
							</div>
						</div>
						<div class="flex flex-col items-end gap-2">
							<p class="font-extrabold text-[15px] text-white">{sub.currency} {Number(sub.amount).toLocaleString()}</p>
							<button
								on:click={() => (confirmDeleteId = sub.id)}
								class="text-[10px] font-bold text-red-500 hover:text-red-400 bg-red-500/10 px-2 py-1 rounded-lg transition-colors"
							>
								Dar de Baja
							</button>
						</div>
					</div>
				</Card>
			{:else}
				<EmptyState title="Sin suscripciones" subtitle="Cargá un servicio para automatizar su cobro." />
			{/each}
		{/if}
	</div>
</main>

<ConfirmDialog
	open={confirmDeleteId !== null}
	title="¿Dar de baja esta suscripción?"
	confirmLabel="Dar de baja"
	on:confirm={confirmDelete}
	on:cancel={() => (confirmDeleteId = null)}
/>
