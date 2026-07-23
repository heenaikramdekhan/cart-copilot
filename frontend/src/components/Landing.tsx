import { useEffect, useState } from "react";
import { authConfigured } from "../supabase";
import AuthForm from "./AuthForm";
import Logo from "./Logo";

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

export default function Landing() {
  const [linkError, setLinkError] = useState<string | null>(null);

  // Supabase drops auth link errors (like an expired confirmation) into the URL
  // hash. Turn it into one short message and wipe the long hash from the bar.
  useEffect(() => {
    const hash = new URLSearchParams(window.location.hash.slice(1));
    if (hash.get("error")) {
      setLinkError(
        hash.get("error_code") === "otp_expired"
          ? "That email link has expired. Sign up again to get a fresh one."
          : hash.get("error_description") || "Something went wrong with that link.",
      );
      history.replaceState(null, "", window.location.pathname);
    }
  }, []);

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
        {linkError && <p className="notice">{linkError}</p>}
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
