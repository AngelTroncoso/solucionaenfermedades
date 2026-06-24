import { useEffect, useRef, useState } from "react";
import { Pause, Play } from "lucide-react";

type Channel = "SISTEMA" | "QWEN-R" | "QWEN-E" | "QWEN-F" | "DISCOVERY" | "PAPER";

type Line = {
  id: number;
  time: string;
  channel: Channel;
  text: string;
};

const CHANNEL_COLOR: Record<Channel, string> = {
  SISTEMA: "#888888",
  "QWEN-R": "#7B68EE",
  "QWEN-E": "#00D4FF",
  "QWEN-F": "#FF6A00",
  DISCOVERY: "#00FF9F",
  PAPER: "#FFD700",
};

function nowStamp() {
  const d = new Date();
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `2050.06.24 ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

// Scripted demo sequence — each entry is a list of lines emitted as a burst
const SEQUENCES: { channel: Channel; text: string }[][] = [
  [
    { channel: "QWEN-R", text: "Analizando combinación: Montelukast + Dupilumab..." },
    { channel: "QWEN-E", text: "Fitness calculado: 0.847 — Umbral superado ✓" },
    { channel: "DISCOVERY", text: "════════════════════════════════════════" },
    { channel: "DISCOVERY", text: "★ NUEVO DESCUBRIMIENTO REGISTRADO ★" },
    { channel: "DISCOVERY", text: "Fármaco:     Montelukast + Dupilumab" },
    { channel: "DISCOVERY", text: "Enfermedad:  Rinitis Alérgica Crónica" },
    { channel: "DISCOVERY", text: "Mecanismo:   Bloqueo dual IL-4Rα + CYSLT1" },
    { channel: "DISCOVERY", text: "Fitness:     0.847 / 1.000" },
    { channel: "DISCOVERY", text: "Área médica: Inmunología / Alergología" },
    { channel: "PAPER", text: "══ APTO PARA PUBLICACIÓN ACADÉMICA ══" },
    { channel: "PAPER", text: "Journal sugerido: Nature Medicine (IF: 58.7)" },
    { channel: "PAPER", text: "Categoría: Drug Repurposing / Th2 Immunology" },
    { channel: "DISCOVERY", text: "════════════════════════════════════════" },
  ],
  [
    { channel: "QWEN-F", text: "Generación 12: cruzando individuos top-5..." },
    { channel: "SISTEMA", text: "Pipeline Sakana FuGU activo — pool=128" },
    { channel: "QWEN-R", text: "Hipótesis: Omalizumab + Bilastina → Rinitis Perenne" },
    { channel: "QWEN-E", text: "Fitness: 0.823 — sinergia IgE/H1 confirmada" },
  ],
  [
    { channel: "SISTEMA", text: "DashScope endpoint OK — qwen3-235b-a22b" },
    { channel: "QWEN-R", text: "Explorando espacio combinatorio: 45 pares activos" },
    { channel: "QWEN-E", text: "Fitness medio: 0.612  σ=0.09" },
  ],
  [
    { channel: "QWEN-R", text: "Hipótesis: Ketotifeno + Rupatadina → Alergia D. Pteronyssinus" },
    { channel: "QWEN-E", text: "Fitness: 0.812 — mecanismo dual mastocito/PAF" },
    { channel: "PAPER", text: "Journal sugerido: Allergy (IF: 12.4)" },
  ],
  [
    { channel: "QWEN-F", text: "Mutación aleatoria aplicada — diversidad +14%" },
    { channel: "SISTEMA", text: "Checkpoint guardado: gen_012.pkl" },
  ],
];

const TABS: ("ALL" | Channel)[] = ["ALL", "SISTEMA", "QWEN-R", "QWEN-E", "QWEN-F"];

export function Terminal({ height = "26rem" }: { height?: string }) {
  const [lines, setLines] = useState<Line[]>([]);
  const [paused, setPaused] = useState(false);
  const [tab, setTab] = useState<(typeof TABS)[number]>("ALL");
  const [flash, setFlash] = useState<"" | "discovery" | "paper">("");
  const idRef = useRef(0);
  const seqRef = useRef(0);
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (paused) return;
    let cancelled = false;

    const emit = async () => {
      const seq = SEQUENCES[seqRef.current % SEQUENCES.length];
      seqRef.current++;
      for (const entry of seq) {
        if (cancelled || paused) return;
        idRef.current++;
        const line: Line = {
          id: idRef.current,
          time: nowStamp(),
          channel: entry.channel,
          text: entry.text,
        };
        setLines((prev) => [...prev.slice(-200), line]);
        if (entry.channel === "DISCOVERY") {
          setFlash("discovery");
          setTimeout(() => setFlash(""), 350);
        } else if (entry.channel === "PAPER") {
          setFlash("paper");
          setTimeout(() => setFlash(""), 350);
        }
        await new Promise((r) => setTimeout(r, 280));
      }
    };

    emit();
    const iv = setInterval(emit, 4200);
    return () => {
      cancelled = true;
      clearInterval(iv);
    };
  }, [paused]);

  useEffect(() => {
    if (boxRef.current) boxRef.current.scrollTop = boxRef.current.scrollHeight;
  }, [lines]);

  const visible = tab === "ALL" ? lines : lines.filter((l) => l.channel === tab || l.channel === "DISCOVERY" || l.channel === "PAPER");

  return (
    <div
      className={`relative rounded-xl border border-[color:var(--color-qwen)]/30 overflow-hidden ${
        flash === "discovery" ? "flash-discovery" : flash === "paper" ? "flash-paper" : ""
      }`}
      style={{ background: "var(--color-terminal)" }}
    >
      <div className="flex items-center justify-between px-3 py-2 border-b border-[color:var(--color-qwen)]/25 bg-black/40">
        <div className="flex gap-1">
          {TABS.map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`text-[11px] font-mono px-2 py-1 rounded transition-colors ${
                tab === t
                  ? "bg-[color:var(--color-qwen)]/20 text-[color:var(--color-cyber)]"
                  : "text-[color:var(--color-muted-foreground)] hover:text-[color:var(--color-foreground)]"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
        <button
          onClick={() => setPaused((p) => !p)}
          className="flex items-center gap-1.5 text-[11px] font-mono px-2.5 py-1 rounded bg-[color:var(--color-qwen)]/15 text-[color:var(--color-cyber)] hover:bg-[color:var(--color-qwen)]/30 transition-colors"
        >
          {paused ? <Play size={12} /> : <Pause size={12} />}
          {paused ? "REANUDAR" : "PAUSAR"} SIMULACIÓN
        </button>
      </div>

      <div
        ref={boxRef}
        className="scrollbar-thin overflow-y-auto px-3 py-2 font-mono text-[13px] leading-[1.55]"
        style={{ height }}
      >
        {visible.map((l, i) => {
          const isLast = i === visible.length - 1;
          return (
            <div key={l.id} className="whitespace-pre">
              <span style={{ color: "#3d6478" }}>{`> ${l.time} `}</span>
              <span style={{ color: CHANNEL_COLOR[l.channel] }}>[{l.channel}]</span>
              <span style={{ color: CHANNEL_COLOR[l.channel], opacity: 0.92 }}>
                {" "}
                {l.text}
              </span>
              {isLast && <span className="cursor-blink" style={{ color: CHANNEL_COLOR[l.channel] }}>▌</span>}
            </div>
          );
        })}
        {visible.length === 0 && (
          <div className="text-[color:var(--color-muted-foreground)]">
            &gt; Inicializando agentes Qwen...
          </div>
        )}
      </div>
    </div>
  );
}
