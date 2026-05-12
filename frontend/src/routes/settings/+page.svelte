<script lang="ts">
    import { onMount } from 'svelte';

    let usdRate = 1250;
    let btcRate = 63000000;
    let loading = false;
    let success = false;

    async function loadRates() {
        const res = await fetch('http://127.0.0.1:8000/settings/rates/');
        if (res.ok) {
            const rates = await res.json();
            rates.forEach((r: any) => {
                if (r.currency === 'USD') usdRate = parseFloat(r.rate_to_base);
                if (r.currency === 'BTC') btcRate = parseFloat(r.rate_to_base);
            });
        }
    }

    onMount(loadRates);

    async function saveRates() {
        loading = true;
        success = false;
        try {
            await fetch('http://127.0.0.1:8000/settings/rates/', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rates: { "USD": usdRate, "BTC": btcRate }
                })
            });
            success = true;
            setTimeout(() => success = false, 3000);
        } finally {
            loading = false;
        }
    }
</script>

<main class="p-4 max-w-md mx-auto bg-slate-50 min-h-screen">
    <header class="mb-6 flex justify-between items-center">
        <h1 class="text-xl font-bold text-slate-800">Ajustes & Cotizaciones</h1>
        <a href="/" class="text-xs font-bold text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-xl border border-indigo-100">← Volver</a>
    </header>

    <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm space-y-5">
        <div>
            <label class="block text-xs font-bold text-slate-400 uppercase mb-2">Valor Dólar (ARS)</label>
            <input type="number" bind:value={usdRate} class="w-full p-3 bg-slate-50 border border-slate-100 rounded-xl text-lg font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>

        <div>
            <label class="block text-xs font-bold text-slate-400 uppercase mb-2">Valor Bitcoin (ARS)</label>
            <input type="number" bind:value={btcRate} class="w-full p-3 bg-slate-50 border border-slate-100 rounded-xl text-lg font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>

        <button on:click={saveRates} disabled={loading} class="w-full bg-indigo-600 text-white font-bold py-3 rounded-xl shadow-lg">
            {loading ? 'Guardando...' : 'Actualizar Cotizaciones'}
        </button>

        {#if success}
            <p class="text-xs text-emerald-600 font-bold text-center">¡Precios actualizados!</p>
        {/if}
    </div>
</main>