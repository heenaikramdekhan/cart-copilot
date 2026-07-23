/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base URL of the deployed backend. Empty in dev, where Vite proxies /api. */
  readonly VITE_API_BASE?: string;
  /** Supabase project URL, for auth. */
  readonly VITE_SUPABASE_URL?: string;
  /** Supabase public anon key, for auth. Safe to expose; never the service key. */
  readonly VITE_SUPABASE_ANON_KEY?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
