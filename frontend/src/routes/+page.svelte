<script lang="ts">
    import { onMount } from 'svelte';

    let totalBalance = { day_to_day_available: 0, total_assets: 0, total_liabilities: 0, net_worth: 0 };
    let accounts: any[] = [];

    async function fetchData() {
        try {
            const resNet = await fetch('http://127.0.0.1:8000/analytics/net-worth');
            totalBalance = await resNet.json();

            const resAccounts = await fetch('http://127.0.0.1:8000/analytics/balances');
            accounts = await resAccounts.json();
        } catch (err) {
            console.error("Error cargando analíticas:", err);
        }
    }

    onMount(fetchData);

    $: dailyAccounts = accounts.filter(a => a.is_day_to_day);
    $: savingsAccounts = accounts.filter(a => !a.is_day_to_day);
</script>

<main class="p-4 max-w-md mx-auto bg-slate-50 min-h-screen pb-24">
    <header class="mb-6 flex justify-between items-center">
        <div>
            <h1 class="text-2xl font-bold text-slate-800">Kinko</h1>
            <p class="text-slate-500 text-xs">Estado de mis finanzas</p>
        </div>
        <a href="/new" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-4 py-2 rounded-xl text-sm shadow-md transition-all">
            + Gasto
        </a>
    </header>

    <div class="bg-indigo-600 rounded-2xl p-6 text-white shadow-lg mb-4">
        <span class="text-indigo-100 text-xs uppercase tracking-wider font-semibold">Disponible Día a Día</span>
        <h2 class="text-4xl font-bold mt-1">${totalBalance.day_to_day_available.toLocaleString()}</h2>
        
        <div class="mt-4 pt-3 border-t border-indigo-500/60 flex justify-between items-center text-xs">
            <span class="text-indigo-200">Patrimonio Neto Global</span>
            <span class="font-bold text-white">${totalBalance.net_worth.toLocaleString()}</span>
        </div>
    </div>

    <div class="grid grid-cols-2 gap-3 mb-6">
        <div class="bg-white p-3 rounded-xl border border-slate-100 shadow-sm">
            <span class="text-[10px] text-slate-400 font-bold uppercase block">Activos Totales</span>
            <span class="text-sm font-bold text-emerald-600">+${totalBalance.total_assets.toLocaleString()}</span>
        </div>
        <div class="bg-white p-3 rounded-xl border border-slate-100 shadow-sm text-right">
            <span class="text-[10px] text-slate-400 font-bold uppercase block">Pasivos Totales</span>
            <span class="text-sm font-bold text-red-600">-${totalBalance.total_liabilities.toLocaleString()}</span>
        </div>
    </div>

  <div class="grid grid-cols-3 gap-2 mb-3">
        <a href="/accounts" class="bg-white p-3 rounded-xl border border-slate-100 shadow-sm text-center block hover:border-indigo-200 transition-all">
            <span class="block text-lg mb-0.5">💳</span>
            <span class="text-[11px] font-bold text-slate-600 block">Cuentas</span>
        </a>
        <a href="/categories" class="bg-white p-3 rounded-xl border border-slate-100 shadow-sm text-center block hover:border-indigo-200 transition-all">
            <span class="block text-lg mb-0.5">🏷️</span>
            <span class="text-[11px] font-bold text-slate-600 block">Categorías</span>
        </a>
        <a href="/people" class="bg-white p-3 rounded-xl border border-slate-100 shadow-sm text-center block hover:border-indigo-200 transition-all">
            <span class="block text-lg mb-0.5">👥</span>
            <span class="text-[11px] font-bold text-slate-600 block">Amigos</span>
        </a>
    </div>
    <div class="grid grid-cols-2 gap-2 mb-6">
        <a href="/subscriptions" class="bg-white p-2.5 rounded-xl border border-slate-100 shadow-sm text-center block hover:border-indigo-200 transition-all">
            <span class="text-xs font-bold text-slate-600 block">🔄 Suscripciones</span>
        </a>
        <a href="/settings" class="bg-white p-2.5 rounded-xl border border-slate-100 shadow-sm text-center block hover:border-indigo-200 transition-all">
            <span class="text-xs font-bold text-slate-600 block">⚙️ Cotizaciones</span>
        </a>
    </div>

    <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Uso Diario</h3>
    <div class="space-y-2 mb-6">
        {#each dailyAccounts as acc}
            <div class="bg-white p-3 rounded-xl shadow-sm flex justify-between items-center border border-slate-100">
                <div>
                    <p class="font-medium text-slate-800 text-sm">{acc.account_name}</p>
                    <p class="text-[10px] text-slate-400 uppercase">{acc.entity}</p>
                </div>
                <div class="text-right">
                    <p class="font-bold text-sm {acc.balance < 0 ? 'text-red-500' : 'text-slate-800'}">
                        {acc.currency} ${acc.balance.toLocaleString()}
                    </p>
                </div>
            </div>
        {/each}
    </div>

    {#if savingsAccounts.length > 0}
        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Ahorros & Inversiones</h3>
        <div class="space-y-2">
            {#each savingsAccounts as acc}
                <div class="bg-white/60 p-3 rounded-xl flex justify-between items-center border border-dashed border-slate-200">
                    <div>
                        <p class="font-medium text-slate-600 text-sm">{acc.account_name}</p>
                        <p class="text-[10px] text-slate-400 uppercase">{acc.entity}</p>
                    </div>
                    <div class="text-right">
                        <p class="font-bold text-sm text-emerald-600">
                            {acc.currency} ${acc.balance.toLocaleString()}
                        </p>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</main>