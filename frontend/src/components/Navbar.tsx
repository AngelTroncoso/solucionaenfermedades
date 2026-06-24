import { Link } from "@tanstack/react-router";
import { Hexagon } from "lucide-react";

const links = [
  { to: "/", label: "COMMAND CENTER" },
  { to: "/discoveries", label: "DISCOVERIES" },
  { to: "/matrix", label: "MOLECULAR MATRIX" },
  { to: "/papers", label: "PAPERS" },
] as const;

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 backdrop-blur-xl bg-[color:var(--color-background)]/70 border-b border-[color:var(--color-qwen)]/30">
      <div className="absolute inset-x-0 -bottom-px h-px bg-gradient-to-r from-transparent via-[color:var(--color-cyber)] to-transparent opacity-70" />
      <div className="mx-auto max-w-7xl px-4 lg:px-6 h-16 flex items-center justify-between gap-4">
        <Link to="/" className="flex items-center gap-2 font-display text-[color:var(--color-foreground)]">
          <Hexagon className="text-[color:var(--color-qwen)] glow-qwen" size={22} />
          <span className="tracking-widest text-sm sm:text-base">PharmaFuture 2050</span>
        </Link>
        <nav className="hidden md:flex items-center gap-1 font-mono text-[11px] tracking-widest">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              activeOptions={{ exact: l.to === "/" }}
              className="px-3 py-2 rounded text-[color:var(--color-muted-foreground)] hover:text-[color:var(--color-cyber)] transition-colors"
              activeProps={{ className: "px-3 py-2 rounded text-[color:var(--color-cyber)] bg-[color:var(--color-qwen)]/10" }}
            >
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="hidden lg:block">
          <div className="neon-frame">
            <div className="neon-inner px-3 py-1.5 font-mono text-[10px] tracking-widest text-[color:var(--color-foreground)] flex items-center gap-2">
              <Hexagon size={11} className="text-[color:var(--color-qwen)]" />
              <span>POWERED BY</span>
              <span className="text-[color:var(--color-qwen)] font-semibold">QWEN</span>
              <span>×</span>
              <span className="text-[color:var(--color-alibaba)] font-semibold">ALIBABA CLOUD</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
