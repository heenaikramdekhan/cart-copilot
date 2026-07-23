export default function Logo() {
  return (
    <span className="logo" aria-hidden="true">
      {/* A cart whose contents are the comparison value-bars. */}
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="#fff"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <rect x="8.3" y="9.5" width="1.7" height="4.5" rx="0.6" fill="#fff" stroke="none" />
        <rect x="11.3" y="7" width="1.7" height="7" rx="0.6" fill="#fff" stroke="none" />
        <rect x="14.3" y="10.5" width="1.7" height="3.5" rx="0.6" fill="#fff" stroke="none" />
        <path d="M2.5 2.5h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.5" />
        <circle cx="9" cy="20.4" r="1.1" />
        <circle cx="18.4" cy="20.4" r="1.1" />
      </svg>
    </span>
  );
}
