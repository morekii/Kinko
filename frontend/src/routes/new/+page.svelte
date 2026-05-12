<script lang="ts">
    import { onMount } from 'svelte';

    // Listas cargadas desde el backend
    let accounts: any[] = [];
    let categories: any[] = [];
    let people: any[] = [];

    // Tipo de movimiento seleccionado
    let type: 'gasto' | 'ingreso' | 'traspaso' = 'gasto';

    // Estado del formulario
    let description = '';
    let amount = '';
    
    // myAccountId representa la cuenta principal del usuario en la operación:
    // - Para Gasto o Traspaso: es la cuenta de origen (de donde sale el dinero).
    // - Para Ingreso: es la cuenta de destino (a donde entra el dinero).
    let myAccountId = '';
    
    // Destino secundario (para gastos e ingresos)
    let destinationType: 'category' | 'person' = 'category';
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

            // Preseleccionar la primera cuenta disponible por defecto
            if (accounts.length > 0) myAccountId = accounts[0].id;
        } catch (err) {
            errorMessage = 'Error al conectar con el backend para cargar opciones.';
        }
    }

    onMount(loadFormEntities);

    // Manejador al cambiar de pestaña para resetear selecciones incompatibles
    function handleTypeChange(newType: 'gasto' | 'ingreso' | 'traspaso') {
        type = newType;
        destinationId = '';
        errorMessage = '';
        successMessage = '';
    }

    async function handleSubmit() {
        if (!amount || isNaN(Number(amount)) || Number(amount) <= 0) {
            errorMessage = 'Ingresá un monto válido mayor a 0.';
            return;
        }
        if (!myAccountId) {
            errorMessage = 'Seleccioná tu cuenta bancaria o billetera.';
            return;
        }

        // Validaciones específicas para traspasos
        if (type === 'traspaso' && !destinationId) {
            errorMessage = 'Seleccioná la cuenta de destino para el traspaso.';
            return;
        }
        if (type === 'traspaso' && myAccountId == destinationId) {
            errorMessage = 'La cuenta de origen y destino no pueden ser la misma.';
            return;
        }

        loading = true;
        errorMessage = '';
        successMessage = '';

        const parsedAmount = parseFloat(amount);
        let entries: any[] = [];

        if (type === 'gasto') {
            // Salida de mi cuenta (-), Entrada a categoría/persona (+)
            entries = [
                { 
                    account_id: parseInt(myAccountId), 
                    amount: -parsedAmount,
                    base_amount: -parsedAmount 
                },
                { 
                    amount: parsedAmount,
                    base_amount: parsedAmount,
                    category_id: destinationType === 'category' && destinationId ? parseInt(destinationId) : null,
                    person_id: destinationType === 'person' && destinationId ? parseInt(destinationId) : null
                }
            ];
        } else if (type === 'ingreso') {
            // Entrada a mi cuenta (+), Salida de categoría/persona (-)
            entries = [
                { 
                    account_id: parseInt(myAccountId), 
                    amount: parsedAmount,
                    base_amount: parsedAmount 
                },
                { 
                    amount: -parsedAmount,
                    base_amount: -parsedAmount,
                    category_id: destinationType === 'category' && destinationId ? parseInt(destinationId) : null,
                    person_id: destinationType === 'person' && destinationId ? parseInt(destinationId) : null
                }
            ];
        } else if (type === 'traspaso') {
            // Salida de mi cuenta origen (-), Entrada a cuenta destino (+)
            entries = [
                { 
                    account_id: parseInt(myAccountId), 
                    amount: -parsedAmount,
                    base_amount: -parsedAmount 
                },
                { 
                    account_id: parseInt(destinationId), 
                    amount: parsedAmount,
                    base_amount: parsedAmount 
                }
            ];
        }

        // Asignar descripción por defecto si se deja en blanco
        const defaultDescriptions = {
            gasto: 'Gasto general',
            ingreso: 'Ingreso de dinero',
            traspaso: 'Traspaso entre cuentas'
        };

        const payload = {
            description: description.trim() || defaultDescriptions[type],
            entries: entries
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

            successMessage = '¡Movimiento registrado con éxito!';
            
            // Limpiar campos rápidos
            description = '';
            amount = '';
            destinationId = '';
            
            // Ocultar notificación de éxito automáticamente
            setTimeout(() => successMessage = '', 3000);
        } catch (err: any) {
            errorMessage = 'No se pudo registrar el movimiento. Verificá los balances.';
            console.error(err);
        } finally {
            loading = false;
        }
    }
</script>

<main class="p-4 max-w-md mx-auto bg-slate-50 min-h-screen">
    <header class="mb-6 flex justify-between items-center">
        <div>
            <h1 class="text-xl font-bold text-slate-800">Registrar Movimiento</h1>
            <p class="text-xs text-slate-500">Partida doble inteligente</p>
        </div>
        <a href="/" class="text-xs font-bold text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-xl border border-indigo-100">
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

    <div class="flex bg-slate-200/70 p-1 rounded-xl mb-5 gap-1">
        <button 
            type="button" 
            on:click={() => handleTypeChange('gasto')}
            class="flex-1 py-2 text-xs font-bold rounded-lg transition-all {type === 'gasto' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-700'}"
        >
            GASTO
        </button>
        <button 
            type="button" 
            on:click={() => handleTypeChange('ingreso')}
            class="flex-1 py-2 text-xs font-bold rounded-lg transition-all {type === 'ingreso' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-700'}"
        >
            INGRESO
        </button>
        <button 
            type="button" 
            on:click={() => handleTypeChange('traspaso')}
            class="flex-1 py-2 text-xs font-bold rounded-lg transition-all {type === 'traspaso' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-700'}"
        >
            TRASPASO
        </button>
    </div>

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
                placeholder={type === 'ingreso' ? 'Ej. Sueldo, Transferencia asado...' : (type === 'traspaso' ? 'Ej. Pago tarjeta, Fondeo broker...' : 'Ej. Supermercado, Almuerzo, Nafta...')}
                bind:value={description}
                class="w-full py-1 text-slate-700 focus:outline-none text-sm placeholder:text-slate-300"
            />
        </div>

        <div class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm">
            <label for="source" class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
                {type === 'ingreso' ? 'Cuenta Destino (¿A dónde entra?)' : 'Cuenta Origen (¿De dónde sale?)'}
            </label>
            <select id="source" bind:value={myAccountId} class="w-full py-1 text-sm font-medium text-slate-700 bg-transparent focus:outline-none">
                {#each accounts as acc}
                    <option value={acc.id}>
                        {acc.entity} - {acc.name} ({acc.currency})
                    </option>
                {/each}
            </select>
        </div>

        {#if type === 'traspaso'}
            <div class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm">
                <label for="dest-acc" class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Cuenta Destino (Ingreso)</label>
                <select id="dest-acc" bind:value={destinationId} class="w-full py-1 text-sm text-slate-700 bg-transparent focus:outline-none" required>
                    <option value="">Seleccionar cuenta destino...</option>
                    {#each accounts.filter(a => a.id != myAccountId) as acc}
                        <option value={acc.id}>{acc.entity} - {acc.name} ({acc.currency})</option>
                    {/each}
                </select>
            </div>
        {:else}
            <div class="bg-slate-200/60 p-1 rounded-xl flex gap-1 text-xs font-medium text-slate-600">
                <button 
                    type="button" 
                    on:click={() => { destinationType = 'category'; destinationId = ''; }}
                    class="flex-1 py-2 rounded-lg transition-all {destinationType === 'category' ? 'bg-white text-slate-800 shadow-sm font-bold' : ''}"
                >
                    {type === 'ingreso' ? 'Origen / Concepto' : 'Categoría'}
                </button>
                <button 
                    type="button" 
                    on:click={() => { destinationType = 'person'; destinationId = ''; }}
                    class="flex-1 py-2 rounded-lg transition-all {destinationType === 'person' ? 'bg-white text-slate-800 shadow-sm font-bold' : ''}"
                >
                    {type === 'ingreso' ? 'Me transfiere amigo' : 'Asignar / Prestar'}
                </button>
            </div>

            <div class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm">
                {#if destinationType === 'category'}
                    <label for="dest-cat" class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
                        {type === 'ingreso' ? 'Clasificación del Ingreso' : 'Categoría de Gasto'}
                    </label>
                    <select id="dest-cat" bind:value={destinationId} class="w-full py-1 text-sm text-slate-700 bg-transparent focus:outline-none">
                        <option value="">Sin categoría asignada</option>
                        {#each categories as cat}
                            <option value={cat.id}>{cat.name}</option>
                        {/each}
                    </select>
                {:else}
                    <label for="dest-per" class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
                        {type === 'ingreso' ? '¿Quién te está pagando?' : '¿A quién le corresponde?'}
                    </label>
                    <select id="dest-per" bind:value={destinationId} class="w-full py-1 text-sm text-slate-700 bg-transparent focus:outline-none">
                        <option value="">Seleccionar amigo...</option>
                        {#each people as prs}
                            <option value={prs.id}>{prs.name}</option>
                        {/each}
                    </select>
                {/if}
            </div>
        {/if}

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