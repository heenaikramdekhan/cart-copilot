# Email templates

Branded Supabase auth emails for Cart Copilot. Supabase keeps these only in the
dashboard, so the source of truth lives here.

## Where each one goes

Supabase dashboard → **Authentication** → **Email Templates** → pick the
template, set the **Subject heading**, and paste the file's HTML into
**Message body**.

| File | Template | Subject |
|---|---|---|
| `confirm-signup.html` | Confirm signup | `Confirm your email for Cart Copilot` |
| `reset-password.html` | Reset Password | `Reset your Cart Copilot password` |

Magic Link and Invite are intentionally left default: the app uses email and
password sign-in and self-signup, so those templates never send. Add branded
versions here if that changes.

## Template variables used

- `{{ .ConfirmationURL }}` — the real action link Supabase generates.
- `{{ .Data.name }}` — the name captured at signup (`user_metadata.name`). The
  templates fall back to "Hi there," when it is absent (older accounts).

## Note

Where these links land depends on **Authentication → URL Configuration**
(Site URL + Redirect URLs). Keep the Site URL set to the deployed app so the
links return the user to it.
