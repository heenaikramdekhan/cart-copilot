import { authConfigured } from "../supabase";
import AuthForm from "./AuthForm";
import Logo from "./Logo";

type Props = { authError?: string | null };

const FEATURES = [
  {
    title: "Understands you",
    body: "Plain-language requests become budget, category, and must-haves.",
  },
  {
    title: "Compares for real",
    body: "Ranked options with real prices and ratings, side by side.",
  },
  {
    title: "Reasons over the cart",
    body: "Flags duplicates, cheaper sellers, and shipping you pay for twice.",
  },
];

export default function Landing({ authError }: Props) {
  return (
    <div className="landing">
      <div className="landing-hero">
        <h1 className="brand">
          <Logo />
          <span className="brand-name">Cart Copilot</span>
        </h1>
        <p className="landing-tagline">
          Tell it what you need in plain English. It searches real products, compares the options,
          and reasons over your whole cart to catch savings and mismatches.
        </p>
        <ul className="features">
          {FEATURES.map((f) => (
            <li key={f.title} className="feature">
              <strong>{f.title}</strong>
              <span>{f.body}</span>
            </li>
          ))}
        </ul>
        <p className="trust">Real data only. 141,240 genuine customer reviews and real prices.</p>
      </div>

      <div className="landing-auth">
        {authError && <p className="notice">{authError}</p>}
        {authConfigured ? (
          <AuthForm />
        ) : (
          <div className="auth-card">
            <p className="notice">
              Sign-in is not configured yet. Set <code>VITE_SUPABASE_URL</code> and{" "}
              <code>VITE_SUPABASE_ANON_KEY</code>, then reload.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
