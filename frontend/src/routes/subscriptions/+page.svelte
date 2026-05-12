<script lang="ts">
    import { onMount } from 'svelte';

    let subscriptions: any[] = [];
    let accounts: any[] = [];
    let categories: any[] = [];

    let description = '';
    let amount = '';
    let currency = 'ARS';
    let chargeDay = '';
    let suggestedAccountId = '';
    let categoryId = '';
    let loading = false;

    async function loadData() {
        const [resSub, resAcc, resCat] = await Promise.all([
            fetch('http://127.0.0.1:8000/subscriptions'),
            fetch('http://127.0.0.1:8000/accounts'),
            fetch('http://127.0.0.1:8000/categories')
        ]);
        if (resSub.ok) subscriptions = await resSub.json();
        if (resAcc.ok) accounts = await resAcc.json();
        if (resCat.ok) categories = await resCat.json();
    }

    onMount(loadData);

    async function createSubscription() {
        if (!description || !amount || !chargeDay) return;
        loading = true;
        const payload = {
            description, currency,
            amount: parseFloat(amount),
            charge_day: parseInt(chargeDay),
            suggested_account_id: suggestedAccountId ? parseInt(suggestedAccountId) : null,
            category_id: categoryId ? parseInt(categoryId) : null,
            is_active: true
        };

        try {
            const res = await fetch('http://127.0.0.1:8000/subscriptions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                description = ''; amount = ''; chargeDay = '';
                await loadData();
            }
        } finally {
            loading = false;
        }
    }

    async function deleteSubscription(id: int) {
        if (!confirm("¿Eliminar suscripción programada?")) return;
        await fetch(`http://127.0.0.1:8000/subscriptions/${id}`, { method: 'DELETE' });
        await loadData();
    }
</script>

<main class="p-4 max-w-md mx-auto bg-slate-50 min-h-screen">
    <header class="mb-6 flex justify-between items-center">
        <h1 class="text-xl font-bold text-slate-800">Suscripciones Fijas</h1>
        <a href="/" class="text-xs font-bold text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-xl border border-indigo-100">← Volver</a>
    </header>

    <form on:submit|preventDefault={createSubscription} class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm mb-6 space-y-3">
        <div class="grid grid-cols-3 gap-2">
            <input type="text" placeholder="Servicio (Ej. Netflix)" bind:value={description} class="col-span-2 p-2 border border-slate-200 rounded-xl text-sm focus:outline-none" required />
            <input type="number" min="1" max="31" placeholder="Día (1-31)" bind:value={chargeDay} class="p-2 border border-slate-200 rounded-xl text-sm focus:outline-none" required />
        </div>
        
        <div class="grid grid-cols-3 gap-2">
            <input type="number" step="0.01" placeholder="Monto" bind:value={amount} class="col-span-2 p-2 border border-slate-200 rounded-xl text-sm focus:outline-none" required />
            <select bind:value={currency} class="p-2 border border-slate-200 rounded-xl text-sm bg-white focus:outline-none">
                <option value="ARS">ARS</option>
                <option value="USD">USD</option>
            </select>
        </div>

        <div class="grid grid-cols-2 gap-2">
            <select bind:value={suggestedAccountId} class="p-2 border border-slate-200 rounded-xl text-xs bg-white focus:outline-none">
                <option value="">Cuenta sugerida...</option>
                {#each accounts as acc}<option value={acc.id}>{acc.name}</option>{/each}
            </select>
            <select bind:value={categoryId} class="p-2 border border-slate-200 rounded-xl text-xs bg-white focus:outline-none">
                <option value="">Categoría...</option>
                {#each categories as cat}<option value={cat.id}>{cat.name}</option>{/each}
            </select>
        </div>

        <button type="submit" disabled={loading} class="w-full bg-indigo-600 text-white font-bold py-2 rounded-xl text-sm hover:bg-indigo-700">Programar Gasto</button>
    </form>

    <div class="space-y-2">
        {#each subscriptions as sub}
            <div class="bg-white p-3 rounded-xl border border-slate-100 flex justify-between items-center text-sm">
                <div>
                    <span class="font-bold text-slate-800 block">🔄 {sub.description}</span>
                    <span class="text-[11px] text-slate-400 block">Se cobra los días {sub.charge_day}</span>
                </div>
                <div class="text-right flex items-center gap-3">
                    <span class="font-bold text-xs text-indigo-600">{sub.currency} ${sub.amount}</span>
                    <button type="button" on:click={() => deleteSubscription(sub.id)} class="text-slate-300 hover:text-red-500 font-bold">✕</button>
                </div>
            </div>
        {/each}
    </div>
</main>