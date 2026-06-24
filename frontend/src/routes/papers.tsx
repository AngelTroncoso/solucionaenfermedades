import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Download, Copy } from "lucide-react";
import { DISCOVERIES, JOURNALS } from "../lib/discoveries";

export const Route = createFileRoute("/papers")({
  head: () => ({
    meta: [
      { title: "Paper Generator — PharmaFuture 2050" },
      { name: "description", content: "Generador automático de papers académicos para descubrimientos con fitness ≥ 0.80." },
    ],
  }),
  component: PaperGenerator,
});

function suggestedTitle(drug: string, disease: string) {
  return `Repurposing ${drug} as a Combination Therapy for ${disease}: A Computational Discovery Framework`;
}

function abstractFor(drug: string, disease: string, mechanism: string, fitness: number) {
  return `We report the computational identification of ${drug} as a high-fitness repurposing candidate for ${disease} (fitness=${fitness.toFixed(
    3,
  )}). Using an evolutionary loop powered by qwen3-235b-a22b on Alibaba Cloud DashScope, we screened a multi-agent hypothesis pool and converged on a mechanism of action involving ${mechanism.toLowerCase()}. The combination shows strong in-silico synergy and is proposed for early-phase clinical validation.`;
}

function PaperGenerator() {
  const eligible = DISCOVERIES.filter((d) => d.fitness >= 0.8);
  return (
    <div className="space-y-8">
      <header>
        <h1 className="font-display text-3xl tracking-widest text-[color:var(--color-paper)]" style={{ textShadow: "0 0 24px #FFD70055" }}>
          PAPER GENERATOR
        </h1>
        <p className="font-mono text-xs text-[color:var(--color-muted-foreground)] mt-1">
          Descubrimientos con fitness ≥ 0.80 · {eligible.length} candidatos aptos para publicación
        </p>
      </header>

      {/* Journals legend */}
      <section className="neon-frame">
        <div className="neon-inner p-4">
          <div className="font-mono text-[10px] tracking-widest text-[color:var(--color-muted-foreground)] mb-3">
            ⬡ JOURNALS RECOMENDADOS
          </div>
          <div className="flex flex-wrap gap-2">
            {JOURNALS.map((j) => (
              <div
                key={j.name}
                className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[color:var(--color-paper)]/10 border border-[color:var(--color-paper)]/40 font-mono text-xs"
              >
                <span className="text-[color:var(--color-foreground)]">{j.name}</span>
                <span className="text-[color:var(--color-paper)]">IF: {j.impact}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div className="grid gap-6">
        {eligible.map((d, i) => (
          <motion.div
            key={d.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="neon-frame"
          >
            <div className="neon-inner p-6">
              <div className="flex items-center gap-2 font-mono text-[10px] tracking-widest text-[color:var(--color-paper)]">
                ⬡ DRAFT MANUSCRIPT · FITNESS {d.fitness.toFixed(3)}
              </div>
              <h2 className="mt-3 font-display text-lg md:text-xl text-[color:var(--color-foreground)] leading-snug">
                {suggestedTitle(d.drug, d.disease)}
              </h2>

              <div className="mt-4">
                <div className="font-mono text-[10px] tracking-widest text-[color:var(--color-cyber)] mb-1">ABSTRACT</div>
                <p className="text-sm text-[color:var(--color-foreground)]/85 leading-relaxed">
                  {abstractFor(d.drug, d.disease, d.mechanism, d.fitness)}
                </p>
              </div>

              <div className="mt-4 flex flex-wrap items-center gap-3 text-xs font-mono">
                <span className="text-[color:var(--color-muted-foreground)]">Target journal:</span>
                <span className="px-2 py-1 rounded bg-[color:var(--color-paper)]/15 text-[color:var(--color-paper)] border border-[color:var(--color-paper)]/40">
                  {d.journal} · IF {JOURNALS.find((j) => j.name === d.journal)?.impact ?? "—"}
                </span>
              </div>

              <div className="mt-5 flex flex-wrap gap-2">
                <button className="flex items-center gap-1.5 px-3 py-2 rounded text-xs font-mono bg-[color:var(--color-paper)] text-black hover:opacity-90">
                  <Download size={14} /> Exportar a PDF
                </button>
                <button className="flex items-center gap-1.5 px-3 py-2 rounded text-xs font-mono border border-[color:var(--color-cyber)]/60 text-[color:var(--color-cyber)] hover:bg-[color:var(--color-cyber)]/10">
                  <Copy size={14} /> Copiar BibTeX
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
