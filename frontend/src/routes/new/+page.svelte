<script lang="ts">
	import { onMount } from 'svelte';
	import { Lock } from 'lucide-svelte';
	import {
		getAccounts,
		getCategories,
		getPeople,
		getRates,
		createExpense,
		createIncome,
		createTransfer,
		createDebt,
		createDebtPayment,
		ApiError
	} from '$lib/api';
	import type { Account, Category, Person, ExchangeRate } from '$lib/types';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Input from '$lib/components/Input.svelte';
	import Select from '$lib/components/Select.svelte';
	import Button from '$lib/components/Button.svelte';

	let accounts: Account[] = [];
	let categories: Category[] = [];
	let people: Person[] = [];
	let rates: ExchangeRate[] = [];

	type OperationType = 'gasto' | 'ingreso' | 'transferencia' | 'deuda' | 'pago_deuda';
	let type: OperationType = 'gasto';

	let description = '';
	let amount: number | string = '';
	let feeAmount: number | string = '';
	let feeCategoryId: any = null;
	let selectedCurrency = 'ARS';
	let primaryAccountId: any = null; // cuenta (o entidad, en modo "deuda")
	let selectedCategoryId: any = null;
	let selectedPersonId: any = null;
	let destinationAccountId: any = null;
	let destinationAmountOverride: number | string = '';
	let destinationAmountEdited = false;

	let reserveMoney = false;
	let reserveSourceId: any = null;

	let loading = false;
	let successMessage = '';
	let errorMessage = '';

	async function loadFormHub() {
		try {
			const [accs, cats, ppl, rts] = await Promise.all([
				getAccounts(),
				getCategories(),
				getPeople(),
				getRates()
			]);
			accounts = accs;
			categories = cats;
			people = ppl;
			rates = rts;
			if (accounts.length > 0) {
				primaryAccountId = accounts[0].id;
				selectedCurrency = accounts[0].currency;
			}
		} catch {
			errorMessage = 'Error conectando al backend.';
		}
	}
	onMount(loadFormHub);

	$: selectedAccountObj = accounts.find((a) => a.id == primaryAccountId);
	$: isCreditCard = selectedAccountObj?.type === 'credit_card';
	$: canReserve = isCreditCard && type === 'gasto' && !!selectedAccountObj?.reserve_account_id;
	$: if (!canReserve) reserveMoney = false;

	$: if (primaryAccountId && type !== 'deuda') {
		if (selectedAccountObj) selectedCurrency = selectedAccountObj.currency;
	}
	$: isMultiCurrencyTransfer = (() => {
		if (type !== 'transferencia' || !primaryAccountId || !destinationAccountId) return false;
		const dst = accounts.find((a) => a.id == destinationAccountId);
		return selectedAccountObj && dst && selectedAccountObj.currency !== dst.currency;
	})();

	// Sólo para mostrar una previsualización: el backend hace el cálculo real al guardar.
	function previewRate(curr: string) {
		if (curr === 'ARS') return 1;
		const rateObj = rates.find((r) => r.currency === curr);
		return rateObj ? Number(rateObj.rate_to_base) : null;
	}
	$: destinationPreview = (() => {
		if (!isMultiCurrencyTransfer || !amount) return null;
		const dst = accounts.find((a) => a.id == destinationAccountId);
		const srcRate = previewRate(selectedCurrency);
		const dstRate = dst ? previewRate(dst.currency) : null;
		if (!srcRate || !dstRate) return null;
		return ((Number(amount) * srcRate) / dstRate).toFixed(6);
	})();

	$: if (!isMultiCurrencyTransfer) {
		destinationAmountEdited = false;
		destinationAmountOverride = '';
	}

	function switchMode(newMode: OperationType) {
		type = newMode;
		destinationAccountId = null;
		selectedCategoryId = null;
		selectedPersonId = null;
		feeAmount = '';
		errorMessage = '';
		successMessage = '';
		reserveMoney = false;
		destinationAmountEdited = false;
		destinationAmountOverride = '';
		if (type === 'deuda') selectedCurrency = 'ARS';
	}

	async function submitOperation() {
		if (!amount || parseFloat(amount as string) <= 0) {
			errorMessage = 'Monto ingresado no válido.';
			return;
		}
		if (type !== 'deuda' && !primaryAccountId) {
			errorMessage = 'Seleccioná la cuenta afectada.';
			return;
		}
		if (type === 'transferencia' && (!destinationAccountId || primaryAccountId == destinationAccountId)) {
			errorMessage = 'Cuenta destino inválida.';
			return;
		}
		if ((type === 'deuda' || type === 'pago_deuda') && !selectedPersonId) {
			errorMessage = 'Seleccioná el contacto correspondiente.';
			return;
		}

		loading = true;
		errorMessage = '';
		successMessage = '';
		const val = parseFloat(amount as string);
		const desc = description.trim() || undefined;

		try {
			if (type === 'gasto') {
				await createExpense({
					description: desc,
					amount: val,
					currency: selectedCurrency,
					account_id: Number(primaryAccountId),
					category_id: selectedCategoryId ? Number(selectedCategoryId) : null,
					person_id: selectedPersonId ? Number(selectedPersonId) : null,
					reserve_funds: reserveMoney,
					reserve_source_account_id: reserveSourceId ? Number(reserveSourceId) : null
				});
			} else if (type === 'ingreso') {
				await createIncome({
					description: desc,
					amount: val,
					currency: selectedCurrency,
					account_id: Number(primaryAccountId),
					category_id: selectedCategoryId ? Number(selectedCategoryId) : null,
					person_id: selectedPersonId ? Number(selectedPersonId) : null
				});
			} else if (type === 'transferencia') {
				await createTransfer({
					description: desc,
					amount: val,
					currency: selectedCurrency,
					source_account_id: Number(primaryAccountId),
					destination_account_id: Number(destinationAccountId),
					fee_amount: feeAmount ? parseFloat(feeAmount as string) : 0,
					fee_category_id: feeCategoryId ? Number(feeCategoryId) : null,
					destination_amount:
						destinationAmountEdited && destinationAmountOverride !== ''
							? parseFloat(destinationAmountOverride as string)
							: null
				});
			} else if (type === 'deuda') {
				await createDebt({
					description: desc,
					amount: val,
					currency: selectedCurrency,
					person_id: Number(primaryAccountId),
					category_id: selectedCategoryId ? Number(selectedCategoryId) : null
				});
			} else if (type === 'pago_deuda') {
				await createDebtPayment({
					description: desc,
					amount: val,
					currency: selectedCurrency,
					account_id: Number(primaryAccountId),
					person_id: Number(selectedPersonId)
				});
			}

			successMessage = '¡Operación registrada con éxito!';
			description = '';
			amount = '';
			feeAmount = '';
			selectedCategoryId = null;
			selectedPersonId = null;
			destinationAccountId = null;
			reserveMoney = false;
			setTimeout(() => (successMessage = ''), 3000);
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo procesar la transacción.';
		} finally {
			loading = false;
		}
	}
</script>

<main class="p-4 max-w-md mx-auto pt-6 pb-28">
	<PageHeader title="Cargar Operación" />

	{#if successMessage}
		<div
			class="p-3 mb-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-card text-xs font-bold text-center animate-fade-in"
		>
			{successMessage}
		</div>
	{/if}
	{#if errorMessage}
		<div
			class="p-3 mb-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-card text-xs font-bold text-center animate-fade-in"
		>
			{errorMessage}
		</div>
	{/if}

	<div class="flex bg-surface border border-zinc-800 p-1 rounded-xl gap-0.5 mb-4 overflow-x-auto no-scrollbar">
		<button
			type="button"
			on:click={() => switchMode('gasto')}
			class="flex-1 min-w-[65px] py-1.5 text-[9px] font-bold uppercase rounded-lg transition-all {type === 'gasto'
				? 'bg-zinc-800 text-white shadow-sm border border-zinc-700'
				: 'text-zinc-500'}">GASTO</button
		>
		<button
			type="button"
			on:click={() => switchMode('ingreso')}
			class="flex-1 min-w-[65px] py-1.5 text-[9px] font-bold uppercase rounded-lg transition-all {type === 'ingreso'
				? 'bg-zinc-800 text-white shadow-sm border border-zinc-700'
				: 'text-zinc-500'}">INGRESO</button
		>
		<button
			type="button"
			on:click={() => switchMode('transferencia')}
			class="flex-1 min-w-[65px] py-1.5 text-[9px] font-bold uppercase rounded-lg transition-all {type ===
			'transferencia'
				? 'bg-zinc-800 text-white shadow-sm border border-zinc-700'
				: 'text-zinc-500'}">TRANSF.</button
		>
		<button
			type="button"
			on:click={() => switchMode('deuda')}
			class="flex-1 min-w-[65px] py-1.5 text-[9px] font-bold uppercase rounded-lg transition-all {type === 'deuda'
				? 'bg-red-600 text-white shadow-sm'
				: 'text-zinc-500'}">A PAGAR</button
		>
		<button
			type="button"
			on:click={() => switchMode('pago_deuda')}
			class="flex-1 min-w-[65px] py-1.5 text-[9px] font-bold uppercase rounded-lg transition-all {type ===
			'pago_deuda'
				? 'bg-emerald-600 text-white shadow-sm'
				: 'text-zinc-500'}">SALDAR</button
		>
	</div>

	<form on:submit|preventDefault={submitOperation} class="space-y-3">
		<div class="bg-surface p-3.5 rounded-card border border-zinc-800 shadow-sm flex justify-between items-center gap-2">
			<div class="flex-1">
				<label for="op-amount" class="block text-[10px] font-bold text-zinc-500 uppercase mb-1"
					>Monto {isMultiCurrencyTransfer ? 'Origen' : ''}</label
				>
				<input
					id="op-amount"
					type="number"
					step="any"
					placeholder="0"
					bind:value={amount}
					class="w-full text-2xl font-bold text-white bg-transparent focus:outline-none"
					required
				/>
			</div>
			<div class="w-24 border-l border-zinc-800 pl-2">
				<label for="op-currency" class="block text-[9px] font-bold text-zinc-500 uppercase mb-1">Divisa</label>
				<select id="op-currency" bind:value={selectedCurrency} class="w-full text-xs font-bold text-blue-500 bg-transparent focus:outline-none">
					<option value="ARS" class="bg-zinc-950 text-white">ARS</option>
					<option value="USD" class="bg-zinc-950 text-white">USD</option>
					<option value="USD_TARJETA" class="bg-zinc-950 text-white">USD Tarjeta</option>
					<option value="USDT" class="bg-zinc-950 text-white">USDT</option>
					<option value="BTC" class="bg-zinc-950 text-white">BTC</option>
				</select>
			</div>
		</div>

		{#if isMultiCurrencyTransfer}
			<div class="bg-blue-950/30 p-3.5 rounded-card border border-blue-900 shadow-sm animate-fade-in">
				<span class="block text-[10px] font-bold text-blue-400 uppercase mb-1">Monto a recibir (destino)</span>
				<div class="flex items-center justify-between gap-2">
					<input
						type="number"
						step="any"
						placeholder={destinationPreview ?? '0'}
						value={destinationAmountEdited ? destinationAmountOverride : (destinationPreview ?? '')}
						on:input={(e) => {
							destinationAmountEdited = true;
							destinationAmountOverride = e.currentTarget.value;
						}}
						class="text-xl font-bold text-white bg-transparent focus:outline-none w-full"
					/>
					<span class="text-xs font-extrabold text-blue-400 bg-zinc-900 px-2 py-1 rounded border border-zinc-800 shadow-sm">
						{accounts.find((a) => a.id == destinationAccountId)?.currency}
					</span>
				</div>
				<p class="text-[9px] text-blue-400/70 mt-1">
					{destinationAmountEdited
						? 'Vas a registrar exactamente este monto recibido.'
						: 'Estimado con la cotización cargada en Configuración — editalo si comprás a un precio distinto.'}
				</p>
			</div>
		{/if}

		<Input label="Concepto" placeholder="Detalle de la operación..." bind:value={description} />

		{#if type === 'transferencia'}
			<Select label="Cuenta Origen" bind:value={primaryAccountId}>
				{#each accounts as acc}<option value={acc.id} class="bg-zinc-950">💳 {acc.entity} - {acc.name}</option>{/each}
			</Select>
			<Select label="Cuenta Destino" bind:value={destinationAccountId} required>
				<option value={null} class="bg-zinc-950">Selec. destino...</option>
				{#each accounts.filter((a) => a.id != primaryAccountId) as acc}<option value={acc.id} class="bg-zinc-950">💳 {acc.entity} - {acc.name}</option>{/each}
			</Select>
			<div class="bg-red-950/20 p-3.5 rounded-card border border-red-900 shadow-sm">
				<label for="op-fee" class="block text-[10px] font-bold text-red-400 uppercase mb-1">Tasas / Impuestos Bancarios (Opcional)</label>
				<div class="flex gap-2">
					<input
						id="op-fee"
						type="number"
						step="any"
						placeholder="0"
						bind:value={feeAmount}
						class="w-24 p-2 bg-zinc-950 rounded-lg text-sm font-bold border border-zinc-800 focus:outline-none text-white"
					/>
					<select bind:value={feeCategoryId} class="flex-1 text-xs text-white bg-zinc-950 border border-zinc-800 rounded-lg px-2 focus:outline-none">
						<option value={null}>Sin categorizar...</option>
						{#each categories as cat}<option value={cat.id}>{cat.name}</option>{/each}
					</select>
				</div>
			</div>
		{:else}
			<Select
				label={type === 'deuda'
					? 'Acreedor (Contacto)'
					: type === 'pago_deuda'
						? 'Cuenta Origen (Para pagar)'
						: type === 'ingreso'
							? 'Cuenta Receptora'
							: 'Cuenta de Pago'}
				bind:value={primaryAccountId}
				required
			>
				<option value={null} class="bg-zinc-950">Seleccionar...</option>
				{#if type === 'deuda'}
					{#each people as p}<option value={p.id} class="bg-zinc-950">🏢 {p.name}</option>{/each}
				{:else}
					{#each accounts as acc}<option value={acc.id} class="bg-zinc-950">💳 {acc.entity} - {acc.name}</option>{/each}
				{/if}
			</Select>

			{#if canReserve}
				<div class="bg-indigo-950/30 p-3.5 rounded-card border border-indigo-900 shadow-sm mt-2 animate-fade-in">
					<label class="flex items-center gap-2 cursor-pointer text-xs font-bold text-indigo-400 uppercase">
						<input type="checkbox" bind:checked={reserveMoney} class="rounded text-indigo-600 bg-zinc-950 border-zinc-800" />
						<Lock size={14} />
						<span>Reservar plata para el resumen</span>
					</label>
					<p class="text-[9px] text-indigo-400/70 mt-1.5">
						Esto transfiere la plata ahora mismo a la cuenta de reserva. Si preferís que siga
						generando rendimiento hasta que llegue el resumen, dejalo destildado y pagá la
						tarjeta con una Transferencia manual cuando llegue.
					</p>
					{#if reserveMoney}
						<div class="mt-3 pt-3 border-t border-indigo-900">
							<span class="text-[9px] font-bold text-indigo-400 uppercase block mb-1">Origen del dinero a reservar</span>
							<select bind:value={reserveSourceId} class="w-full text-xs text-white bg-zinc-950 border border-zinc-800 p-1.5 rounded focus:outline-none">
								<option value={null}>Cuenta principal (por defecto)</option>
								{#each accounts.filter((a) => a.type !== 'credit_card') as acc}<option value={acc.id}>{acc.entity} - {acc.name}</option>{/each}
							</select>
						</div>
					{/if}
				</div>
			{/if}

			<div class="grid grid-cols-2 gap-2 mt-2">
				<Select label="Categoría" bind:value={selectedCategoryId}>
					<option value={null} class="bg-zinc-950">Ninguna</option>
					{#each categories as cat}<option value={cat.id} class="bg-zinc-950">🏷️ {cat.name}</option>{/each}
				</Select>
				<Select label="Contacto" bind:value={selectedPersonId} required={type === 'pago_deuda'}>
					<option value={null} class="bg-zinc-950">Ninguna</option>
					{#each people as p}<option value={p.id} class="bg-zinc-950">🏢 {p.name}</option>{/each}
				</Select>
			</div>
		{/if}

		<Button type="submit" disabled={loading}>{loading ? 'Procesando...' : 'Confirmar Movimiento'}</Button>
	</form>
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
