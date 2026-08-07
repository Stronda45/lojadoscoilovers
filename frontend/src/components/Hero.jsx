// Ilustração placeholder (Fase 1) — SVG inline, sem foto de banco de imagens
// (evita risco de licença e mantém o bundle autocontido).
function CoiloverIllustration() {
  return (
    <svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <g transform="translate(30,10)" stroke="rgba(255,255,255,0.85)" strokeWidth="3" fill="none">
        <rect x="26" y="0" width="8" height="14" rx="2" fill="rgba(255,255,255,0.85)" stroke="none" />
        <path d="M30 14 C10 20, 50 26, 30 32 C10 38, 50 44, 30 50 C10 56, 50 62, 30 68 C10 74, 50 80, 30 86" />
        <rect x="26" y="86" width="8" height="14" rx="2" fill="rgba(255,255,255,0.85)" stroke="none" />
      </g>
      <g transform="translate(110,10)" stroke="rgba(255,255,255,0.55)" strokeWidth="3" fill="none">
        <rect x="26" y="0" width="8" height="14" rx="2" fill="rgba(255,255,255,0.55)" stroke="none" />
        <path d="M30 14 C10 20, 50 26, 30 32 C10 38, 50 44, 30 50 C10 56, 50 62, 30 68 C10 74, 50 80, 30 86" />
        <rect x="26" y="86" width="8" height="14" rx="2" fill="rgba(255,255,255,0.55)" stroke="none" />
      </g>
    </svg>
  );
}

export default function Hero() {
  return (
    <div className="hero">
      <div className="hero__text">
        <h1>Suspensões e peças pro seu carro</h1>
        <p>Selecione marca, modelo e motorização — preço e estoque na hora.</p>
      </div>
      <div className="hero__illustration">
        <CoiloverIllustration />
      </div>
    </div>
  );
}
