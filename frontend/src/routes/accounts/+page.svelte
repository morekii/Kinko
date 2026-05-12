<script lang="ts">
    import { onMount } from 'svelte';

    let accounts: any[] = [];
    let name = '';
    let entity = '';
    let type = 'savings';
    let currency = 'ARS';
    let isDayToDay = true;
    let closingDay = '';
    let dueDay = '';
    let loading = false;

    async function loadAccounts() {
        const res = await fetch('http://127.0.0.1:8000/accounts');
        if (res.ok) accounts = await res.json();
    }

    onMount(loadAccounts);

    async function createAccount() {
        if (!name || !entity) return;
        loading = true;
        const payload: any = {
            name, entity, type, currency,
            is_day_to_day: isDayToDay,
            is_active: true
        };
        if (type === 'credit_card') {
            payload.closing_day = closingDay ? parseInt(closingDay) : null;
            payload.due_day = dueDay ? parseInt(dueDay) : null;
        }

        try {
            const res = await fetch('http://127.0.0.1:8000/accounts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                name = ''; entity = ''; closingDay = ''; dueDay = '';
                await loadAccounts();
            }
        } finally {
            loading = false;
        }
    }

    async function deleteAccount(id: int) {
        if (!confirm("¿Desactivar cuenta? Sus saldos históricos se mantendrán intactos.")) return;
        await fetch(`http://127.0.0.1:8000/accounts/${id}`, { method: 'DELETE' });
        await loadAccounts();
    }
</script>

<main class="p-4 max-w-md mx-auto bg-slate-50 min-h-screen">
    <header class="mb-6 flex justify-between items-center">
        <h1 class="text-xl font-bold text-slate-800">Mis Cuentas</h1>
        <a href="/" class="text-xs font-bold text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-xl border border-indigo-100">← Volver</a>
    </header>

    <form on:submit|preventDefault={createAccount} class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm mb-6 space-y-3">
        <div class="grid grid-cols-2 gap-2">
            <input type="text" placeholder="Nombre (Ej. Visa)" bind:value={name} class="p-2 border border-slate-200 rounded-xl text-sm focus:outline-none" required />
            <input type="text" placeholder="Banco/App (Ej. Galicia)" bind:value={entity} class="p-2 border border-slate-200 rounded-xl text-sm focus:outline-none" required />
        </div>
        
        <div class="grid grid-cols-2 gap-2">
            <select bind:value={type} class="p-2 border border-slate-200 rounded-xl text-sm bg-white focus:outline-none">
                <option value="savings">Ahorro / Débito</option>
                <option value="credit_card">Tarjeta de Crédito</option>
                <option value="cash">Efectivo</option>
                <option value="virtual">Billetera Virtual</option>
            </select>
            <select bind:value={currency} class="p-2 border border-slate-200 rounded-xl text-sm bg-white focus:outline-none">
                <option value="ARS">ARS ($)</option>
                <option value="USD">USD (u$s)</option>
                <option value="USDT">USDT</option>
                <option value="BTC">BTC (₿)</option>
            </select>
        </div>

        {#if type === 'credit_card'}
            <div class="grid grid-cols-2 gap-2 bg-slate-50 p-2 rounded-xl border border-slate-100">
                <div>
                    <label class="block text-[10px] font-bold text-slate-400 uppercase">Día Cierre</label>
                    <input type="number" min="1" max="31" placeholder="Ej. 25" bind:value={closingDay} class="w-full p-1 bg-white border border-slate-200 rounded-lg text-xs" />
                </div>
                <div>
                    <label class="block text-[10px] font-bold text-slate-400 uppercase">Día Vencim.</label>
                    <input type="number" min="1" max="31" placeholder="Ej. 5" bind:value={dueDay} class="w-full p-1 bg-white border border-slate-200 rounded-lg text-xs" />
                </div>
            </div>
        {/if}

        <label class="flex items-center gap-2 pt-1 text-xs text-slate-600 font-medium cursor-pointer">
            <input type="checkbox" bind:checked={isDayToDay} class="rounded text-indigo-600 w-4 h-4" />
            <span>¿Suma al disponible Día a Día?</span>
        </label>

        <button type="submit" disabled={loading} class="w-full bg-slate-800 text-white font-bold py-2 rounded-xl text-sm hover:bg-slate-900">Agregar Cuenta</button>
    </form>

    <div class="space-y-2">
        {#each accounts as acc}
            <div class="bg-white p-3 rounded-xl border border-slate-100 flex justify-between items-center text-sm">
                <div>
                    <span class="font-bold text-slate-800 block">{acc.name}</span>
                    <span class="text-[11px] text-slate-400 block">{acc.entity} • {acc.type}</span>
                </div>
                <div class="text-right flex items-center gap-3">
                    <span class="text-xs font-semibold px-2 py-0.5 rounded-md {acc.is_day_to_day ? 'bg-indigo-50 text-indigo-600' : 'bg-slate-100 text-slate-600'}">
                        {acc.currency}
                    </span>
                    <button type="button" on:click={() => deleteAccount(acc.id)} class="text-slate-300 hover:text-red-500 font-bold">✕</button>
                </div>
            </div>
        {/each}
    </div>
</main>