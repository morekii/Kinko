<script lang="ts">
    import "../app.css";
    import { page } from '$app/stores';
    
    let isSidebarOpen = false;

    function toggleSidebar() {
        isSidebarOpen = !isSidebarOpen;
    }

    function closeSidebar() {
        isSidebarOpen = false;
    }
</script>

<div class="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
    <header class="bg-indigo-600 text-white px-4 py-3 flex justify-between items-center shadow-md sticky top-0 z-40">
        <div class="flex items-center gap-3">
            <button on:click={toggleSidebar} class="p-1 hover:bg-indigo-700 rounded-lg focus:outline-none transition-colors" aria-label="Abrir menú de navegación">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
            </button>
            <span class="font-bold text-lg tracking-wide">Kinko</span>
        </div>
        
        {#if $page.url.pathname !== '/new'}
            <a href="/new" class="bg-emerald-500 hover:bg-emerald-600 text-white font-bold px-3 py-1.5 rounded-xl text-xs shadow transition-all">
                + Movimiento
            </a>
        {/if}
    </header>

    {#if isSidebarOpen}
        <button 
            type="button"
            on:click={closeSidebar} 
            class="fixed inset-0 bg-black/50 w-full h-full cursor-default border-none focus:outline-none z-50 transition-opacity animate-fade-in block"
            aria-label="Cerrar menú lateral"
        ></button>
    {/if}

    <aside class="fixed top-0 left-0 bottom-0 w-64 bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col {isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}">
        <div class="p-5 bg-indigo-600 text-white flex justify-between items-center">
            <div>
                <h2 class="font-bold text-lg">Menú Kinko</h2>
                <p class="text-[10px] text-indigo-200">Navegación general</p>
            </div>
            <button on:click={closeSidebar} class="text-indigo-200 hover:text-white font-bold text-lg" aria-label="Cerrar panel">✕</button>
        </div>

        <nav class="flex-1 p-4 space-y-1 overflow-y-auto text-sm font-medium">
            <a href="/" on:click={closeSidebar} class="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors {$page.url.pathname === '/' ? 'bg-indigo-50 text-indigo-600 font-bold' : 'text-slate-600'}">
                <span>🏠</span> Dashboard Principal
            </a>
            <a href="/search" on:click={closeSidebar} class="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors {$page.url.pathname === '/search' ? 'bg-indigo-50 text-indigo-600 font-bold' : 'text-slate-600'}">
                <span>🔍</span> Buscar Gastos
            </a>
            <a href="/accounts" on:click={closeSidebar} class="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors {$page.url.pathname === '/accounts' ? 'bg-indigo-50 text-indigo-600 font-bold' : 'text-slate-600'}">
                <span>💳</span> Mis Cuentas
            </a>
            <a href="/categories" on:click={closeSidebar} class="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors {$page.url.pathname === '/categories' ? 'bg-indigo-50 text-indigo-600 font-bold' : 'text-slate-600'}">
                <span>🏷️</span> Categorías
            </a>
            <a href="/entities" on:click={closeSidebar} class="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors {$page.url.pathname.startsWith('/entities') ? 'bg-indigo-50 text-indigo-600 font-bold' : 'text-slate-600'}">
                <span>🏢</span> Entidades & Préstamos
            </a>
            <a href="/subscriptions" on:click={closeSidebar} class="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors {$page.url.pathname === '/subscriptions' ? 'bg-indigo-50 text-indigo-600 font-bold' : 'text-slate-600'}">
                <span>🔄</span> Gastos Programados
            </a>
            <a href="/settings" on:click={closeSidebar} class="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors {$page.url.pathname === '/settings' ? 'bg-indigo-50 text-indigo-600 font-bold' : 'text-slate-600'}">
                <span>⚙️</span> Cotizaciones Manuales
            </a>
        </nav>

        <div class="p-4 border-t border-slate-100 text-center">
            <span class="text-[10px] text-slate-400 font-semibold block">Kinko v1.0 • Partida Doble</span>
        </div>
    </aside>

    <div class="flex-1">
        <slot />
    </div>
</div>