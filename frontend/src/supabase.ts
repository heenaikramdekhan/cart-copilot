import { createClient } from "@supabase/supabase-js";

// The public anon key is safe in the browser; it only grants what Supabase's
// row-level security allows. The service key stays on the backend, never here.
const url = import.meta.env.VITE_SUPABASE_URL ?? "";
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY ?? "";

/** True only when both auth env vars are set, so the UI can explain if they are not. */
export const authConfigured = Boolean(url && anonKey);

// Placeholders keep createClient from throwing when the env vars are missing;
// authConfigured gates any real auth call, so the app shows a clear notice
// instead of a blank screen.
export const supabase = createClient(
  url || "https://placeholder.supabase.co",
  anonKey || "placeholder-anon-key",
);
