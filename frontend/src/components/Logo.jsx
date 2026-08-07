// Ícone placeholder (Fase 1) — mola de suspensão estilizada, SVG inline
// (sem dependência externa, sem risco de licença).
export default function Logo({ size = 28 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <rect x="14" y="1" width="4" height="6" rx="1" fill="currentColor" />
      <rect x="14" y="25" width="4" height="6" rx="1" fill="currentColor" />
      <path
        d="M16 7 C8 9, 24 11, 16 13 C8 15, 24 17, 16 19 C8 21, 24 23, 16 25"
        stroke="currentColor"
        strokeWidth="2.4"
        strokeLinecap="round"
        fill="none"
      />
    </svg>
  );
}
