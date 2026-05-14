
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	type MatcherParam<M> = M extends (param : string) => param is (infer U extends string) ? U : string;

	export interface AppTypes {
		RouteId(): "/" | "/accounts" | "/accounts/[id]" | "/categories" | "/categories/[id]" | "/entities" | "/entities/[id]" | "/new" | "/search" | "/settings" | "/subscriptions" | "/transactions" | "/transactions/[id]";
		RouteParams(): {
			"/accounts/[id]": { id: string };
			"/categories/[id]": { id: string };
			"/entities/[id]": { id: string };
			"/transactions/[id]": { id: string }
		};
		LayoutParams(): {
			"/": { id?: string };
			"/accounts": { id?: string };
			"/accounts/[id]": { id: string };
			"/categories": { id?: string };
			"/categories/[id]": { id: string };
			"/entities": { id?: string };
			"/entities/[id]": { id: string };
			"/new": Record<string, never>;
			"/search": Record<string, never>;
			"/settings": Record<string, never>;
			"/subscriptions": Record<string, never>;
			"/transactions": { id?: string };
			"/transactions/[id]": { id: string }
		};
		Pathname(): "/" | "/accounts" | `/accounts/${string}` & {} | "/categories" | `/categories/${string}` & {} | "/entities" | `/entities/${string}` & {} | "/new" | "/search" | "/settings" | "/subscriptions" | "/transactions" | `/transactions/${string}` & {};
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): string & {};
	}
}