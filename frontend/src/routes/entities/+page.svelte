<script lang="ts">
    import { onMount } from 'svelte';
    let entities: any[] = []; 
    let name = ''; 
    let isDebtTracker = false; // Checkbox para control patrimonial
    let loading = false;

    async function loadEnts() {
        const res = await fetch('http://127.0.0.1:8000/people');
        if (res.ok) entities = await res.json();
    }
    onMount(loadEnts);

    async function addEnt() {
        if (!name.trim()) return;
        loading = true;
        await fetch('http://127.0.0.1:8000/people', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name.trim(), is_debt_tracker: isDebtTracker, is_active: true })
        });
        name = ''; isDebtTracker = false; loading = false; 
        await loadEnts();
    }
</script>

<main class="p-4 max-w-md mx-auto space-y-4">
    <header class="flex justify-between items-center">
        <h1 class="text-xl font-bold text-slate-800">Entidades & Deudas</h1>
        <button type="button" on:click={() => history.back()} class="text-xs font-bold text-indigo-600 px-3 py-1.5 bg-indigo-50 rounded-xl">← Volver</button>
    </header>

    <form on:submit|preventDefault={addEnt} class="bg-white p-3 rounded-2xl border border-slate-100 shadow-sm space-y-2">
        <div class="flex gap-2">
            <input type="text" placeholder="Nombre (Ej. Empleador, Mati...)" bind:value={name} class="flex-1 p-2 bg-slate-50 border border-slate-100 rounded-lg text-xs focus:outline-none" required />
            <button type="submit" disabled={loading} class="bg-indigo-600 text-white font-bold px-3 rounded-lg text-xs">Crear</button>
        </div>
        <label class="flex items-center gap-1.5 px-1 cursor-pointer text-[10px] text-slate-500 font-medium">
            <input type="checkbox" bind:checked={isDebtTracker} class="rounded text-indigo-600" />
            <span>Rastrear saldo en Activos / Pasivos (Cuenta Corriente real)</span>
        </label>
    </form>

    <div class="space-y-2">
        {#each entities as ent}
            <a href="/entities/{ent.id}" class="bg-white p-3.5 rounded-xl border border-slate-100 shadow-sm flex justify-between items-center block hover:border-indigo-100 transition-all">
                <div>
                    <div class="flex items-center gap-1.5">
                        <span class="font-bold text-xs text-slate-800 block">🏢 {ent.name}</span>
                        {#if ent.is_debt_tracker}
                            <span class="bg-amber-100 text-amber-800 text-[8px] font-extrabold px-1.5 py-0.5 rounded">PATRIMONIAL</span>
                        {/if}
                    </div>
                    <span class="text-[9px] text-slate-400 block mt-0.5">Ver historial contable</span>
                </div>
                <div class="text-right">
                    <span class="font-extrabold text-xs block {ent.balance > 0 ? 'text-emerald-600' : ent.balance < 0 ? 'text-red-600' : 'text-slate-600'}">
                        ${parseFloat(ent.balance).toLocaleString()}
                    </span>
                    <span class="text-[8px] text-slate-400 block uppercase">
                        {ent.balance > 0 ? 'A cobrar' : ent.balance < 0 ? 'A pagar' : 'Saldado'}
                    </span>
                </div>
            </a>
        {/each}
    </div>
</main>