import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, FileText, X } from "lucide-react";
import { DISCOVERIES, type Discovery } from "../lib/discoveries";

export const Route = createFileRoute("/discoveries")({
  head: () => ({
    meta: [
      { title: "Discovery Feed — PharmaFuture 2050" },
      { name: "description", content: "Timeline de descubrimientos farmacéuticos generados por agentes Qwen." },
    ],
  }),
  component: DiscoveryFeed,
});

const STATUS_COLOR: Record<Discovery["status"], string> = {
  NUEVO: "#00D4FF",
  "EN REVISIÓN": "#FFD700",
  PUBLICABLE: "#00FF9F",
  ARCHIVADO: "#6b88a8",
};

function fitnessColor(f: number) {
  if (f >= 0.8) return "#00FF9F";
  if (f >= 0.7) return "#FFD700";
  return "#ff6a6a";
}

function DiscoveryCard({ d, onPaper }: { d: Discovery; onPaper: (d: Discovery) => void }) {
  const [open, setOpen] = useState(false);
  return (
    <motion.article
      initial={{ opacity: 0, x: -16 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.45 }}
      className="neon-frame"
    >
      <div className="neon-inner p-5">
        <div className="flex flex-wrap items-center gap-3 text-xs font-mono">
          <span className="text-[color:var(--color-muted-foreground)]">{d.timestamp}</span>
          <span
            className="px-2 py-0.5 rounded text-[10px] tracking-widest"
            style={{ background: STATUS_COLOR[d.status] + "22", color: STATUS_COLOR[d.status], border: `1px solid ${STATUS_COLOR[d.status]}55` }}
          >
            {d.status}
          </span>
          <span className="ml-auto text-[color:var(--color-muted-foreground)]">{d.area}</span>
        </div>

        <h3 className="mt-3 font-display text-xl md:text-2xl tracking-wide text-[color:var(--color-foreground)]">
          {d.drug}
        </h3>
        <p className="text-sm text-[color:var(--color-cyber)] font-mono">→ {d.disease}</p>

        <div className="mt-4">
          <div className="flex items-center justify-between text-[11px] font-mono mb-1.5">
            <span className="text-[color:var(--color-muted-foreground)]">FITNESS SCORE</span>
            <span style={{ color: fitnessColor(d.fitness) }}>{d.fitness.toFixed(3)} / 1.000</span>
          </div>
          <div className="h-2 rounded-full bg-black/50 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              whileInView={{ width: `${d.fitness * 100}%` }}
              viewport={{ once: true }}
              transition={{ duration: 1.2 }}
              className="h-full rounded-full"
              style={{
                background: `linear-gradient(90deg, #ff3b6b 0%, #FFD700 50%, ${fitnessColor(d.fitness)} 100%)`,
                boxShadow: `0 0 12px ${fitnessColor(d.fitness)}66`,
              }}
            />
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <button
            onClick={() => setOpen((v) => !v)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono bg-[color:var(--color-qwen)]/15 text-[color:var(--color-qwen)] hover:bg-[color:var(--color-qwen)]/25"
          >
            <ChevronDown size={14} className={open ? "rotate-180 transition-transform" : "transition-transform"} />
            Ver Mecanismo Molecular
          </button>
          <button
            disabled={!d.paper}
            onClick={() => onPaper(d)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono bg-[color:var(--color-paper)]/10 text-[color:var(--color-paper)] hover:bg-[color:var(--color-paper)]/25 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <FileText size={14} />
            Evaluar para Paper
          </button>
        </div>

        <AnimatePresence>
          {open && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-4 p-3 rounded border border-[color:var(--color-qwen)]/30 bg-black/30 font-mono text-xs text-[color:var(--color-foreground)]/90">
                <div className="text-[color:var(--color-cyber)] mb-1">[MECANISMO MOLECULAR]</div>
                {d.mechanism}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.article>
  );
}

function PaperModal({ d, onClose }: { d: Discovery; onClose: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 grid place-items-center bg-black/70 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.92, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.95 }}
        onClick={(e) => e.stopPropagation()}
        className="neon-frame max-w-lg w-full"
      >
        <div className="neon-inner p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="font-mono text-[10px] tracking-widest text-[color:var(--color-paper)]">
                ══ APTO PARA PUBLICACIÓN ACADÉMICA ══
              </div>
              <h3 className="mt-2 font-display text-lg text-[color:var(--color-foreground)]">{d.drug}</h3>
              <p className="text-sm text-[color:var(--color-cyber)] font-mono">{d.disease}</p>
            </div>
            <button onClick={onClose} className="text-[color:var(--color-muted-foreground)] hover:text-white">
              <X size={18} />
            </button>
          </div>
          <div className="mt-4 space-y-2 font-mono text-xs">
            <div><span className="text-[color:var(--color-muted-foreground)]">Journal sugerido: </span><span className="text-[color:var(--color-paper)]">{d.journal}</span></div>
            <div><span className="text-[color:var(--color-muted-foreground)]">Fitness: </span><span className="text-[color:var(--color-discovery)]">{d.fitness.toFixed(3)}</span></div>
            <div><span className="text-[color:var(--color-muted-foreground)]">Área: </span>{d.area}</div>
            <div className="pt-2 text-[color:var(--color-foreground)]/85">{d.mechanism}</div>
          </div>
          <div className="mt-5 flex gap-2">
            <button className="flex-1 py-2 rounded text-xs font-mono bg-[color:var(--color-paper)] text-black hover:opacity-90">Exportar a PDF</button>
            <button className="flex-1 py-2 rounded text-xs font-mono border border-[color:var(--color-paper)]/60 text-[color:var(--color-paper)] hover:bg-[color:var(--color-paper)]/10">Copiar BibTeX</button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

function DiscoveryFeed() {
  const [paperDoc, setPaperDoc] = useState<Discovery | null>(null);
  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-display text-3xl tracking-widest text-[color:var(--color-qwen)] glow-qwen">DISCOVERY FEED</h1>
        <p className="font-mono text-xs text-[color:var(--color-muted-foreground)] mt-1">
          Timeline en tiempo real · {DISCOVERIES.length} descubrimientos registrados
        </p>
      </header>
      <div className="space-y-4">
        {DISCOVERIES.map((d) => (
          <DiscoveryCard key={d.id} d={d} onPaper={setPaperDoc} />
        ))}
      </div>
      <AnimatePresence>
        {paperDoc && <PaperModal d={paperDoc} onClose={() => setPaperDoc(null)} />}
      </AnimatePresence>
    </div>
  );
}
