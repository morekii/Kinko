<script lang="ts">
    import { onMount } from 'svelte';

    // Listas cargadas desde el backend
    let accounts: any[] = [];
    let categories: any[] = [];
    let people: any[] = [];

    // Estado del formulario
    let description = '';
    let amount = '';
    let sourceAccountId = '';
    
    // Tipo de destino para simplificar la UI móvil
    let destinationType: 'category' | 'account' | 'person' = 'category';
    let destinationId = '';

    // Estado de la UI
    let loading = false;
    let successMessage = '';
    let errorMessage = '';

    async function loadFormEntities() {
        try {
            const [resAcc, resCat, resPpl] = await Promise.all([
                fetch('http://127.0.0.1:8000/accounts'),
                fetch('http://127.0.0.1:8000/categories'),
                fetch('http://127.0.0.1:8000/people')
            ]);
            accounts = await resAcc.json();
            categories = await resCat.json();
            people = await resPpl.json();

            // Preseleccionar la primera cuenta por defecto si existe
            if (accounts.length > 0) sourceAccountId = accounts[0].id;
        } catch (err) {
            errorMessage = 'Error al conectar con el backend para cargar opciones.';
        }
    }

    onMount(loadFormEntities);

    async function handleSubmit() {
        if (!amount || isNaN(Number(amount)) || Number(amount) <= 0) {
            errorMessage = 'Ingresá un monto válido mayor a 0.';
            return;
        }
        if (!sourceAccountId) {
            errorMessage = 'Seleccioná una cuenta de origen.';
            return;
        }

        loading = true;
        errorMessage = '';
        successMessage = '';

        const parsedAmount = parseFloat(amount);

        // Construimos la partida doble de forma transparente para el usuario
        // Pata 1: Salida de la cuenta origen (negativo)
        const entrySource = {
            account_id: parseInt(sourceAccountId),
            amount: -parsedAmount,
            base_amount: -parsedAmount // Asumimos misma moneda por ahora para simplificar carga rápida
        };

        // Pata 2: Entrada al destino (positivo)
        const entryDestination: any = {
            amount: parsedAmount,
            base_amount: parsedAmount
        };

        if (destinationType === 'category') {
            entryDestination.category_id = destinationId ? parseInt(destinationId) : null;
        } else if (destinationType === 'account') {
            entryDestination.account_id = destinationId ? parseInt(destinationId) : null;
        } else if (destinationType === 'person') {
            entryDestination.person_id = destinationId ? parseInt(destinationId) : null;
        }

        const payload = {
            description: description || 'Gasto sin descripción',
            entries: [entrySource, entryDestination]
        };

        try {
            const res = await fetch('http://127.0.0.1:8000/transactions/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(JSON.stringify(errData));
            }

            successMessage = '¡Transacción registrada con éxito!';
            // Reset de campos rápidos
            description = '';
            amount = '';
            destinationId = '';
        } catch (err: any) {
            errorMessage = 'No se pudo registrar la transacción. Verificá los balances.';
            console.error(err);
        } finally {
            loading = false;
        }
    }
</script>

<main class="p-4 max-w-md mx-auto bg-slate-50 min-h-screen">
    <header class="mb-6 flex justify-between items-center">
        <div>
            <h1 class="text-xl font-bold text-slate-800">Nuevo Movimiento</h1>
            <p class="text-xs text-slate-500">Carga rápida con partida doble</p>
        </div>
        <a href="/" class="text-sm font-semibold text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-xl border border-indigo-100">
            ← Volver
        </a>
    </header>

    {#if successMessage}
        <div class="bg-emerald-50 border border-emerald-200 text-emerald-700 p-4 rounded-xl mb-4 text-sm font-medium animate-fade-in">
            {successMessage}
        </div>
    {/if}

    {#if errorMessage}
        <div class="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl mb-4 text-sm font-medium">
            {errorMessage}
        </div>
    {/if}

    <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        <div class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm">
            <label for="amount" class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Monto</label>
            <div class="relative flex items-center">
                <span class="absolute left-3 text-slate-400 font-bold text-lg">$</span>
                <input 
                    id="amount"
                    type="number" 
                    step="0.01"
                    inputmode="decimal"
                    placeholder="0.00"
                    bind:value={amount}
                    class="w-full pl-8 pr-4 py-2 text-2xl font-bold text-slate-800 focus:outline-none placeholder:text-slate-300"
                    required
                />
            </div>
        </div>

        <div class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm">
            <label for="description" class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Descripción</label>
            <input 
                id="description"
                type="text" 
                placeholder="Ej. Supermercado, Almuerzo, Nafta..."
                bind:value={description}
                class="w-full py-1 text-slate-700 focus:outline-none text-sm placeholder:text-slate-300"
            />
        </div>

        <div class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm">
            <label for="source" class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Cuenta Origen (Salida)</label>
            <select id="source" bind:value={sourceAccountId} class="w-full py-1 text-sm font-medium text-slate-700 bg-transparent focus:outline-none">
                {#each accounts as acc}
                    <option value={acc.id}>
                        {acc.entity} - {acc.name} ({acc.currency})
                    </option>
                {/each}
            </select>
        </div>

        <div class="bg-slate-200/60 p-1 rounded-xl flex gap-1 text-xs font-medium text-slate-600">
            <button 
                type="button" 
                on:click={() => { destinationType = 'category'; destinationId = ''; }}
                class="flex-1 py-2 rounded-lg transition-all {destinationType === 'category' ? 'bg-white text-slate-800 shadow-sm font-bold' : ''}"
            >
                Categoría
            </button>
            <button 
                type="button" 
                on:click={() => { destinationType = 'account'; destinationId = ''; }}
                class="flex-1 py-2 rounded-lg transition-all {destinationType === 'account' ? 'bg-white text-slate-800 shadow-sm font-bold' : ''}"
            >
                Traspaso
            </button>
            <button 
                type="button" 
                on:click={() => { destinationType = 'person'; destinationId = ''; }}
                class="flex-1 py-2 rounded-lg transition-all {destinationType === 'person' ? 'bg-white text-slate-800 shadow-sm font-bold' : ''}"
            >
                Amigo/Deuda
            </button>
        </div>

        <div class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm">
            {#if destinationType === 'category'}
                <label for="dest-cat" class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Categoría de Gasto</label>
                <select id="dest-cat" bind:value={destinationId} class="w-full py-1 text-sm text-slate-700 bg-transparent focus:outline-none">
                    <option value="">Sin categoría asignada</option>
                    {#each categories as cat}
                        <option value={cat.id}>{cat.name}</option>
                    {/each}
                </select>
            {:else if destinationType === 'account'}
                <label for="dest-acc" class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Cuenta Destino (Ingreso)</label>
                <select id="dest-acc" bind:value={destinationId} class="w-full py-1 text-sm text-slate-700 bg-transparent focus:outline-none">
                    <option value="">Seleccionar cuenta...</option>
                    {#each accounts.filter(a => a.id != sourceAccountId) as acc}
                        <option value={acc.id}>{acc.entity} - {acc.name}</option>
                    {/each}
                </select>
            {:else}
                <label for="dest-per" class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Prestar o Asignar a Persona</label>
                <select id="dest-per" bind:value={destinationId} class="w-full py-1 text-sm text-slate-700 bg-transparent focus:outline-none">
                    <option value="">Seleccionar amigo...</option>
                    {#each people as prs}
                        <option value={prs.id}>{prs.name}</option>
                    {/each}
                </select>
            {/if}
        </div>

        <button 
            type="submit" 
            disabled={loading}
            class="w-full mt-2 bg-indigo-600 hover:bg-indigo-700 active:scale-[0.99] text-white font-bold py-3 rounded-2xl shadow-lg shadow-indigo-600/20 transition-all flex justify-center items-center gap-2"
        >
            {#if loading}
                <span class="inline-block w-4 h-4 border-2 border-white/60 border-t-white rounded-full animate-spin"></span>
                Procesando...
            {:else}
                Registrar Movimiento
            {/if}
        </button>
    </form>
</main>