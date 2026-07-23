/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base URL of the deployed backend. Empty in dev, where Vite proxies /api. */
  readonly VITE_API_BASE?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
