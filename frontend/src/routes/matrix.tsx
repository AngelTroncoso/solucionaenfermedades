import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { MOLECULES } from "../lib/discoveries";

export const Route = createFileRoute("/matrix")({
  head: () => ({
    meta: [
      { title: "Molecular Matrix — PharmaFuture 2050" },
      { name: "description", content: "Base de datos de fármacos aprobados visualizada en grid hexagonal." },
    ],
  }),
  component: MolecularMatrix,
});

function MolecularMatrix() {
  return (
    <div className="space-y-8">
      <header>
        <h1 className="font-display text-3xl tracking-widest text-[color:var(--color-qwen)] glow-qwen">MOLECULAR MATRIX</h1>
        <p className="font-mono text-xs text-[color:var(--color-muted-foreground)] mt-1">
          Base de datos · 10 fármacos aprobados disponibles para reposicionamiento
        </p>
      </header>

      <div className="grid gap-6 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        {MOLECULES.map((m, i) => {
          const isGeneric = m.patent === "genérico";
          return (
            <motion.div
              key={m.name}
              initial={{ opacity: 0, scale: 0.85 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05, duration: 0.4 }}
              className="group relative aspect-[1/1.05]"
            >
              <div
                className="hex absolute inset-0 transition-all duration-300 group-hover:scale-105"
                style={{
                  background: "linear-gradient(135deg, #7B68EE 0%, #00D4FF 50%, #FF6A00 100%)",
                  filter: "drop-shadow(0 0 8px rgba(123,104,238,0.4))",
                }}
              />
              <div
                className="hex absolute inset-[2px] flex flex-col items-center justify-center p-3 text-center"
                style={{ background: "var(--color-surface)" }}
              >
                <div className="font-display text-[13px] leading-tight text-[color:var(--color-foreground)]">
                  {m.name}
                </div>
                <div className="mt-1 font-mono text-[10px] text-[color:var(--color-cyber)]">
                  {m.target}
                </div>
                <span
                  className="mt-2 px-1.5 py-0.5 rounded text-[9px] font-mono tracking-wider"
                  style={{
                    background: isGeneric ? "#00FF9F22" : "#ff3b6b22",
                    color: isGeneric ? "#00FF9F" : "#ff6a6a",
                    border: `1px solid ${isGeneric ? "#00FF9F66" : "#ff3b6b66"}`,
                  }}
                >
                  {isGeneric ? "GENÉRICO" : "VIGENTE"}
                </span>
              </div>
              {/* tooltip */}
              <div className="pointer-events-none absolute left-1/2 -translate-x-1/2 top-full mt-2 w-56 opacity-0 group-hover:opacity-100 transition-opacity z-20">
                <div className="rounded border border-[color:var(--color-qwen)]/50 bg-black/90 p-2 font-mono text-[11px] text-[color:var(--color-foreground)]/90 shadow-xl">
                  <span className="text-[color:var(--color-cyber)]">[MoA] </span>
                  {m.moa}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
