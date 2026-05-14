<script lang="ts">
    import { onMount } from 'svelte';
    let rates = { blue: 1250, mep: 1200, tarjeta: 1550, oficial: 950, btc: 63000000 };
    let success = false;

    async function save() {
        const res = await fetch('http://127.0.0.1:8000/settings/rates/', {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                rates: { 
                    "USD_BLUE": rates.blue, 
                    "USD_MEP": rates.mep, 
                    "USD_TARJETA": rates.tarjeta,
                    "USD_OFICIAL": rates.oficial,
                    "BTC": rates.btc 
                }
            })
        });
        if (res.ok) { success = true; setTimeout(() => success = false, 3000); }
    }
</script>

<main class="p-4 max-w-md mx-auto bg-slate-50 min-h-screen">
    <header class="mb-6 flex justify-between items-center">
        <h1 class="text-xl font-bold text-slate-800">Cotizaciones</h1>
        <a href="/" class="text-xs font-bold text-indigo-600">← Volver</a>
    </header>

    <div class="bg-white p-5 rounded-2xl shadow-sm space-y-4 border border-slate-100">
        {#each Object.entries(rates) as [key, val]}
            <div>
                <label class="block text-[10px] font-bold text-slate-400 uppercase mb-1">USD {key}</label>
                <input type="number" bind:value={rates[key]} class="w-full p-2 bg-slate-50 border border-slate-100 rounded-lg font-bold" />
            </div>
        {/each}
        <button on:click={save} class="w-full bg-indigo-600 text-white font-bold py-3 rounded-xl shadow-lg mt-4">Guardar Cambios</button>
        {#if success}<p class="text-center text-xs text-emerald-600 font-bold">¡Precios actualizados!</p>{/if}
    </div>
</main>