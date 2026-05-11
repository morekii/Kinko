<script lang="ts">
    import { onMount } from 'svelte';

    let totalBalance = { total_assets: 0, total_liabilities: 0, net_worth: 0 };
    let accounts = [];

    async function fetchData() {
        // Llamadas al backend (FastAPI)
        const resNet = await fetch('http://127.0.0.1:8000/analytics/net-worth');
        totalBalance = await resNet.json();

        const resAccounts = await fetch('http://127.0.0.1:8000/analytics/balances');
        accounts = await resAccounts.json();
    }

    onMount(fetchData);
</script>

<main class="p-4 max-w-md mx-auto bg-slate-50 min-h-screen">
    <header class="mb-8">
        <h1 class="text-2xl font-bold text-slate-800">Kinko</h1>
        <p class="text-slate-500">Estado de mis finanzas</p>
    </header>

    <div class="bg-indigo-600 rounded-2xl p-6 text-white shadow-lg mb-6">
        <span class="text-indigo-100 text-sm">Patrimonio Neto</span>
        <h2 class="text-4xl font-bold mt-1">${totalBalance.net_worth.toLocaleString()}</h2>
        
        <div class="flex justify-between mt-6 pt-4 border-t border-indigo-500">
            <div>
                <p class="text-indigo-200 text-xs uppercase tracking-wider">Activos</p>
                <p class="font-semibold">+${totalBalance.total_assets.toLocaleString()}</p>
            </div>
            <div class="text-right">
                <p class="text-indigo-200 text-xs uppercase tracking-wider">Pasivos</p>
                <p class="font-semibold">-${totalBalance.total_liabilities.toLocaleString()}</p>
            </div>
        </div>
    </div>

    <h3 class="text-lg font-bold text-slate-700 mb-3">Mis Cuentas</h3>
    <div class="space-y-3">
        {#each accounts as acc}
            <div class="bg-white p-4 rounded-xl shadow-sm flex justify-between items-center border border-slate-100">
                <div>
                    <p class="font-medium text-slate-800">{acc.account_name}</p>
                    <p class="text-xs text-slate-400 uppercase">{acc.entity}</p>
                </div>
                <div class="text-right">
                    <p class="font-bold {acc.balance < 0 ? 'text-red-500' : 'text-emerald-500'}">
                        ${acc.balance.toLocaleString()}
                    </p>
                </div>
            </div>
        {/each}
    </div>
</main>