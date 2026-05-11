
// this file is generated — do not edit it


/// <reference types="@sveltejs/kit" />

/**
 * This module provides access to environment variables that are injected _statically_ into your bundle at build time and are limited to _private_ access.
 * 
 * |         | Runtime                                                                    | Build time                                                               |
 * | ------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
 * | Private | [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private) | [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private) |
 * | Public  | [`$env/dynamic/public`](https://svelte.dev/docs/kit/$env-dynamic-public)   | [`$env/static/public`](https://svelte.dev/docs/kit/$env-static-public)   |
 * 
 * Static environment variables are [loaded by Vite](https://vitejs.dev/guide/env-and-mode.html#env-files) from `.env` files and `process.env` at build time and then statically injected into your bundle at build time, enabling optimisations like dead code elimination.
 * 
 * **_Private_ access:**
 * 
 * - This module cannot be imported into client-side code
 * - This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured)
 * 
 * For example, given the following build time environment:
 * 
 * ```env
 * ENVIRONMENT=production
 * PUBLIC_BASE_URL=http://site.com
 * ```
 * 
 * With the default `publicPrefix` and `privatePrefix`:
 * 
 * ```ts
 * import { ENVIRONMENT, PUBLIC_BASE_URL } from '$env/static/private';
 * 
 * console.log(ENVIRONMENT); // => "production"
 * console.log(PUBLIC_BASE_URL); // => throws error during build
 * ```
 * 
 * The above values will be the same _even if_ different values for `ENVIRONMENT` or `PUBLIC_BASE_URL` are set at runtime, as they are statically replaced in your code with their build time values.
 */
declare module '$env/static/private' {
	export const SHELL: string;
	export const npm_command: string;
	export const LSCOLORS: string;
	export const npm_config_userconfig: string;
	export const COLORTERM: string;
	export const XDG_CONFIG_DIRS: string;
	export const npm_config_cache: string;
	export const LESS: string;
	export const XDG_SESSION_PATH: string;
	export const MACHTYPE: string;
	export const G_BROKEN_FILENAMES: string;
	export const HOSTNAME: string;
	export const HISTSIZE: string;
	export const MINICOM: string;
	export const NODE: string;
	export const NODE_OPTIONS: string;
	export const AUDIODRIVER: string;
	export const JRE_HOME: string;
	export const XDG_DATA_HOME: string;
	export const CPU: string;
	export const XDG_CONFIG_HOME: string;
	export const COLOR: string;
	export const npm_config_local_prefix: string;
	export const DESKTOP_SESSION: string;
	export const KITTY_PID: string;
	export const npm_config_globalconfig: string;
	export const XCURSOR_SIZE: string;
	export const GPG_TTY: string;
	export const EDITOR: string;
	export const XDG_SEAT: string;
	export const PWD: string;
	export const QEMU_AUDIO_DRV: string;
	export const XDG_SESSION_DESKTOP: string;
	export const LOGNAME: string;
	export const XDG_SESSION_TYPE: string;
	export const MANPATH: string;
	export const npm_config_init_module: string;
	export const SYSTEMD_EXEC_PID: string;
	export const _: string;
	export const DESKTOP_STARTUP_ID: string;
	export const KITTY_PUBLIC_KEY: string;
	export const LS_OPTIONS: string;
	export const XKEYSYMDB: string;
	export const XNLSPATH: string;
	export const HOME: string;
	export const LANG: string;
	export const LS_COLORS: string;
	export const XDG_CURRENT_DESKTOP: string;
	export const npm_package_version: string;
	export const PYTHONSTARTUP: string;
	export const STARSHIP_SHELL: string;
	export const WAYLAND_DISPLAY: string;
	export const KITTY_WINDOW_ID: string;
	export const OSTYPE: string;
	export const XDG_SEAT_PATH: string;
	export const LESS_ADVANCED_PREPROCESSOR: string;
	export const INVOCATION_ID: string;
	export const NIRI_SOCKET: string;
	export const MANAGERPID: string;
	export const INIT_CWD: string;
	export const STARSHIP_SESSION_KEY: string;
	export const XDG_CACHE_HOME: string;
	export const npm_lifecycle_script: string;
	export const MOZ_GMP_PATH: string;
	export const npm_config_npm_version: string;
	export const LESSCLOSE: string;
	export const XDG_SESSION_CLASS: string;
	export const ANDROID_HOME: string;
	export const OLLAMA_HOST: string;
	export const TERMINFO: string;
	export const TERM: string;
	export const npm_package_name: string;
	export const ZSH: string;
	export const G_FILENAME_ENCODING: string;
	export const HOST: string;
	export const npm_config_prefix: string;
	export const XAUTHLOCALHOSTNAME: string;
	export const ZDOTDIR: string;
	export const LESSOPEN: string;
	export const USER: string;
	export const PAM_KWALLET5_LOGIN: string;
	export const MORE: string;
	export const CSHEDIT: string;
	export const DISPLAY: string;
	export const npm_lifecycle_event: string;
	export const SHLVL: string;
	export const WINDOWMANAGER: string;
	export const PAGER: string;
	export const XDG_VTNR: string;
	export const XDG_SESSION_ID: string;
	export const MANAGERPIDFDID: string;
	export const npm_config_user_agent: string;
	export const XDG_STATE_HOME: string;
	export const npm_execpath: string;
	export const XDG_RUNTIME_DIR: string;
	export const DEBUGINFOD_URLS: string;
	export const npm_package_json: string;
	export const JOURNAL_STREAM: string;
	export const MANPATHISSET: string;
	export const XCURSOR_THEME: string;
	export const XDG_DATA_DIRS: string;
	export const GDK_BACKEND: string;
	export const npm_config_noproxy: string;
	export const VENDOR: string;
	export const CONFIG_SITE: string;
	export const PATH: string;
	export const npm_config_node_gyp: string;
	export const GTK_USE_PORTAL: string;
	export const DBUS_SESSION_BUS_ADDRESS: string;
	export const PROFILEREAD: string;
	export const npm_config_global_prefix: string;
	export const MAIL: string;
	export const HOSTTYPE: string;
	export const NODE_VERSION: string;
	export const KITTY_INSTALLATION_DIR: string;
	export const npm_node_execpath: string;
	export const LESSKEY: string;
	export const OLDPWD: string;
	export const NODE_ENV: string;
}

/**
 * This module provides access to environment variables that are injected _statically_ into your bundle at build time and are _publicly_ accessible.
 * 
 * |         | Runtime                                                                    | Build time                                                               |
 * | ------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
 * | Private | [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private) | [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private) |
 * | Public  | [`$env/dynamic/public`](https://svelte.dev/docs/kit/$env-dynamic-public)   | [`$env/static/public`](https://svelte.dev/docs/kit/$env-static-public)   |
 * 
 * Static environment variables are [loaded by Vite](https://vitejs.dev/guide/env-and-mode.html#env-files) from `.env` files and `process.env` at build time and then statically injected into your bundle at build time, enabling optimisations like dead code elimination.
 * 
 * **_Public_ access:**
 * 
 * - This module _can_ be imported into client-side code
 * - **Only** variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`) are included
 * 
 * For example, given the following build time environment:
 * 
 * ```env
 * ENVIRONMENT=production
 * PUBLIC_BASE_URL=http://site.com
 * ```
 * 
 * With the default `publicPrefix` and `privatePrefix`:
 * 
 * ```ts
 * import { ENVIRONMENT, PUBLIC_BASE_URL } from '$env/static/public';
 * 
 * console.log(ENVIRONMENT); // => throws error during build
 * console.log(PUBLIC_BASE_URL); // => "http://site.com"
 * ```
 * 
 * The above values will be the same _even if_ different values for `ENVIRONMENT` or `PUBLIC_BASE_URL` are set at runtime, as they are statically replaced in your code with their build time values.
 */
declare module '$env/static/public' {
	
}

/**
 * This module provides access to environment variables set _dynamically_ at runtime and that are limited to _private_ access.
 * 
 * |         | Runtime                                                                    | Build time                                                               |
 * | ------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
 * | Private | [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private) | [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private) |
 * | Public  | [`$env/dynamic/public`](https://svelte.dev/docs/kit/$env-dynamic-public)   | [`$env/static/public`](https://svelte.dev/docs/kit/$env-static-public)   |
 * 
 * Dynamic environment variables are defined by the platform you're running on. For example if you're using [`adapter-node`](https://github.com/sveltejs/kit/tree/main/packages/adapter-node) (or running [`vite preview`](https://svelte.dev/docs/kit/cli)), this is equivalent to `process.env`.
 * 
 * **_Private_ access:**
 * 
 * - This module cannot be imported into client-side code
 * - This module includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured)
 * 
 * > [!NOTE] In `dev`, `$env/dynamic` includes environment variables from `.env`. In `prod`, this behavior will depend on your adapter.
 * 
 * > [!NOTE] To get correct types, environment variables referenced in your code should be declared (for example in an `.env` file), even if they don't have a value until the app is deployed:
 * >
 * > ```env
 * > MY_FEATURE_FLAG=
 * > ```
 * >
 * > You can override `.env` values from the command line like so:
 * >
 * > ```sh
 * > MY_FEATURE_FLAG="enabled" npm run dev
 * > ```
 * 
 * For example, given the following runtime environment:
 * 
 * ```env
 * ENVIRONMENT=production
 * PUBLIC_BASE_URL=http://site.com
 * ```
 * 
 * With the default `publicPrefix` and `privatePrefix`:
 * 
 * ```ts
 * import { env } from '$env/dynamic/private';
 * 
 * console.log(env.ENVIRONMENT); // => "production"
 * console.log(env.PUBLIC_BASE_URL); // => undefined
 * ```
 */
declare module '$env/dynamic/private' {
	export const env: {
		SHELL: string;
		npm_command: string;
		LSCOLORS: string;
		npm_config_userconfig: string;
		COLORTERM: string;
		XDG_CONFIG_DIRS: string;
		npm_config_cache: string;
		LESS: string;
		XDG_SESSION_PATH: string;
		MACHTYPE: string;
		G_BROKEN_FILENAMES: string;
		HOSTNAME: string;
		HISTSIZE: string;
		MINICOM: string;
		NODE: string;
		NODE_OPTIONS: string;
		AUDIODRIVER: string;
		JRE_HOME: string;
		XDG_DATA_HOME: string;
		CPU: string;
		XDG_CONFIG_HOME: string;
		COLOR: string;
		npm_config_local_prefix: string;
		DESKTOP_SESSION: string;
		KITTY_PID: string;
		npm_config_globalconfig: string;
		XCURSOR_SIZE: string;
		GPG_TTY: string;
		EDITOR: string;
		XDG_SEAT: string;
		PWD: string;
		QEMU_AUDIO_DRV: string;
		XDG_SESSION_DESKTOP: string;
		LOGNAME: string;
		XDG_SESSION_TYPE: string;
		MANPATH: string;
		npm_config_init_module: string;
		SYSTEMD_EXEC_PID: string;
		_: string;
		DESKTOP_STARTUP_ID: string;
		KITTY_PUBLIC_KEY: string;
		LS_OPTIONS: string;
		XKEYSYMDB: string;
		XNLSPATH: string;
		HOME: string;
		LANG: string;
		LS_COLORS: string;
		XDG_CURRENT_DESKTOP: string;
		npm_package_version: string;
		PYTHONSTARTUP: string;
		STARSHIP_SHELL: string;
		WAYLAND_DISPLAY: string;
		KITTY_WINDOW_ID: string;
		OSTYPE: string;
		XDG_SEAT_PATH: string;
		LESS_ADVANCED_PREPROCESSOR: string;
		INVOCATION_ID: string;
		NIRI_SOCKET: string;
		MANAGERPID: string;
		INIT_CWD: string;
		STARSHIP_SESSION_KEY: string;
		XDG_CACHE_HOME: string;
		npm_lifecycle_script: string;
		MOZ_GMP_PATH: string;
		npm_config_npm_version: string;
		LESSCLOSE: string;
		XDG_SESSION_CLASS: string;
		ANDROID_HOME: string;
		OLLAMA_HOST: string;
		TERMINFO: string;
		TERM: string;
		npm_package_name: string;
		ZSH: string;
		G_FILENAME_ENCODING: string;
		HOST: string;
		npm_config_prefix: string;
		XAUTHLOCALHOSTNAME: string;
		ZDOTDIR: string;
		LESSOPEN: string;
		USER: string;
		PAM_KWALLET5_LOGIN: string;
		MORE: string;
		CSHEDIT: string;
		DISPLAY: string;
		npm_lifecycle_event: string;
		SHLVL: string;
		WINDOWMANAGER: string;
		PAGER: string;
		XDG_VTNR: string;
		XDG_SESSION_ID: string;
		MANAGERPIDFDID: string;
		npm_config_user_agent: string;
		XDG_STATE_HOME: string;
		npm_execpath: string;
		XDG_RUNTIME_DIR: string;
		DEBUGINFOD_URLS: string;
		npm_package_json: string;
		JOURNAL_STREAM: string;
		MANPATHISSET: string;
		XCURSOR_THEME: string;
		XDG_DATA_DIRS: string;
		GDK_BACKEND: string;
		npm_config_noproxy: string;
		VENDOR: string;
		CONFIG_SITE: string;
		PATH: string;
		npm_config_node_gyp: string;
		GTK_USE_PORTAL: string;
		DBUS_SESSION_BUS_ADDRESS: string;
		PROFILEREAD: string;
		npm_config_global_prefix: string;
		MAIL: string;
		HOSTTYPE: string;
		NODE_VERSION: string;
		KITTY_INSTALLATION_DIR: string;
		npm_node_execpath: string;
		LESSKEY: string;
		OLDPWD: string;
		NODE_ENV: string;
		[key: `PUBLIC_${string}`]: undefined;
		[key: `${string}`]: string | undefined;
	}
}

/**
 * This module provides access to environment variables set _dynamically_ at runtime and that are _publicly_ accessible.
 * 
 * |         | Runtime                                                                    | Build time                                                               |
 * | ------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
 * | Private | [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private) | [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private) |
 * | Public  | [`$env/dynamic/public`](https://svelte.dev/docs/kit/$env-dynamic-public)   | [`$env/static/public`](https://svelte.dev/docs/kit/$env-static-public)   |
 * 
 * Dynamic environment variables are defined by the platform you're running on. For example if you're using [`adapter-node`](https://github.com/sveltejs/kit/tree/main/packages/adapter-node) (or running [`vite preview`](https://svelte.dev/docs/kit/cli)), this is equivalent to `process.env`.
 * 
 * **_Public_ access:**
 * 
 * - This module _can_ be imported into client-side code
 * - **Only** variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`) are included
 * 
 * > [!NOTE] In `dev`, `$env/dynamic` includes environment variables from `.env`. In `prod`, this behavior will depend on your adapter.
 * 
 * > [!NOTE] To get correct types, environment variables referenced in your code should be declared (for example in an `.env` file), even if they don't have a value until the app is deployed:
 * >
 * > ```env
 * > MY_FEATURE_FLAG=
 * > ```
 * >
 * > You can override `.env` values from the command line like so:
 * >
 * > ```sh
 * > MY_FEATURE_FLAG="enabled" npm run dev
 * > ```
 * 
 * For example, given the following runtime environment:
 * 
 * ```env
 * ENVIRONMENT=production
 * PUBLIC_BASE_URL=http://example.com
 * ```
 * 
 * With the default `publicPrefix` and `privatePrefix`:
 * 
 * ```ts
 * import { env } from '$env/dynamic/public';
 * console.log(env.ENVIRONMENT); // => undefined, not public
 * console.log(env.PUBLIC_BASE_URL); // => "http://example.com"
 * ```
 * 
 * ```
 * 
 * ```
 */
declare module '$env/dynamic/public' {
	export const env: {
		[key: `PUBLIC_${string}`]: string | undefined;
	}
}
