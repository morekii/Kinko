<script lang="ts">
    import { onMount } from 'svelte';
    let accounts: any[] = [];
    let name = ''; let entity = ''; let type = 'savings'; let currency = 'ARS';
    let isDayToDay = true; let loading = false; let showForm = false;

    async function loadAccs() {
        const res = await fetch('http://127.0.0.1:8000/analytics/balances');
        if (res.ok) accounts = await res.json();
    }
    onMount(loadAccs);

    async function addAcc() {
        if (!name || !entity) return;
        loading = true;
        await fetch('http://127.0.0.1:8000/accounts', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, entity, type, currency, is_day_to_day: isDayToDay, is_active: true })
        });
        name = ''; entity = ''; showForm = false; loading = false;
        await loadAccs();
    }
</script>

<main class="p-4 max-w-md mx-auto space-y-4">
    <header class="flex justify-between items-center">
        <h1 class="text-xl font-bold text-slate-800">Administrar Cuentas</h1>
        <button type="button" on:click={() => history.back()} class="text-xs font-bold text-indigo-600 px-3 py-1.5 bg-indigo-50 rounded-xl">← Volver</button>
    </header>

    <div class="space-y-2">
        {#each accounts as acc}
            <a href="/accounts/{acc.account_id}" class="bg-white p-3.5 rounded-xl border border-slate-100 shadow-sm flex justify-between items-center block hover:border-indigo-100">
                <div>
                    <span class="font-bold text-slate-800 text-sm block">{acc.account_name}</span>
                    <span class="text-[10px] text-slate-400 block uppercase">{acc.entity} • {acc.currency}</span>
                </div>
                <div class="text-right">
                    <span class="font-extrabold text-sm block {acc.balance < 0 ? 'text-red-500' : 'text-slate-800'}">${parseFloat(acc.balance).toLocaleString()}</span>
                    <span class="text-[9px] text-indigo-600 block font-semibold">Configurar ⚙️</span>
                </div>
            </a>
        {/each}
    </div>

    <button type="button" on:click={() => showForm = !showForm} class="w-full py-2.5 bg-slate-200/60 font-bold text-slate-700 rounded-xl text-xs">{showForm ? 'Cancelar' : '+ Registrar Nueva Cuenta'}</button>

    {#if showForm}
        <form on:submit|preventDefault={addAcc} class="bg-white p-4 rounded-2xl shadow-md space-y-3">
            <input type="text" placeholder="Nombre (Ej. Débito)" bind:value={name} class="w-full p-2 border rounded-lg text-xs" required />
            <input type="text" placeholder="Entidad (Ej. Banco)" bind:value={entity} class="w-full p-2 border rounded-lg text-xs" required />
            <div class="grid grid-cols-2 gap-2">
                <select bind:value={type} class="p-2 border rounded-lg text-xs bg-white"><option value="savings">Ahorro</option><option value="credit_card">Crédito</option></select>
                <select bind:value={currency} class="p-2 border rounded-lg text-xs bg-white"><option value="ARS">ARS</option><option value="USD">USD</option></select>
            </div>
            <button type="submit" disabled={loading} class="w-full bg-indigo-600 text-white font-bold py-2 rounded-lg text-xs">Crear</button>
        </form>
    {/if}
</main>