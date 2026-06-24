import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Activity, FlaskConical, Sparkles } from "lucide-react";
import { AnimatedCounter } from "../components/AnimatedCounter";
import { Terminal } from "../components/Terminal";
import { DISCOVERIES, FITNESS_EVOLUTION } from "../lib/discoveries";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Command Center — PharmaFuture 2050" },
      { name: "description", content: "Métricas en tiempo real del motor de descubrimiento farmacéutico Qwen × Alibaba Cloud." },
    ],
  }),
  component: CommandCenter,
});

function MetricCard({
  label,
  children,
  accent,
  icon,
}: {
  label: string;
  children: React.ReactNode;
  accent: string;
  icon: React.ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="neon-frame"
    >
      <div className="neon-inner p-5">
        <div className="flex items-center justify-between text-[11px] tracking-widest font-mono text-[color:var(--color-muted-foreground)]">
          <span>{label}</span>
          <span style={{ color: accent }}>{icon}</span>
        </div>
        <div className="mt-3 font-display text-4xl lg:text-5xl" style={{ color: accent, textShadow: `0 0 24px ${accent}55` }}>
          {children}
        </div>
      </div>
    </motion.div>
  );
}

function CommandCenter() {
  const maxFitness = Math.max(...DISCOVERIES.map((d) => d.fitness));
  const publishable = DISCOVERIES.filter((d) => d.paper).length;

  return (
    <div className="space-y-8">
      {/* Hero */}
      <section className="text-center pt-4 pb-2">
        <motion.h1
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="font-display text-4xl md:text-6xl tracking-[0.18em] text-[color:var(--color-qwen)] glow-qwen"
        >
          PHARMAFUTURE 2050
        </motion.h1>
        <p className="mt-3 font-mono text-xs md:text-sm tracking-[0.3em] text-[color:var(--color-muted-foreground)]">
          POWERED BY <span className="text-[color:var(--color-qwen)]">QWEN AI</span> ×{" "}
          <span className="text-[color:var(--color-alibaba)]">ALIBABA CLOUD</span>
        </p>
        <p className="mt-2 font-mono text-[10px] text-[color:var(--color-muted-foreground)]/80">
          Model: qwen3-235b-a22b · Infrastructure: Alibaba Cloud DashScope
        </p>
      </section>

      {/* Metrics */}
      <section className="grid gap-5 md:grid-cols-3">
        <MetricCard label="HIPÓTESIS ACTIVAS" accent="var(--color-cyber)" icon={<Activity size={16} />}>
          <AnimatedCounter value={1284} />
        </MetricCard>
        <MetricCard label="FITNESS MÁXIMO ALCANZADO" accent="var(--color-qwen)" icon={<FlaskConical size={16} />}>
          <div>
            <AnimatedCounter value={maxFitness} decimals={3} />
            <div className="mt-3 h-2 w-full rounded-full bg-black/50 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${maxFitness * 100}%` }}
                transition={{ duration: 1.6, ease: "easeOut" }}
                className="h-full rounded-full"
                style={{
                  background: "linear-gradient(90deg, var(--color-qwen), var(--color-cyber))",
                  boxShadow: "0 0 16px var(--color-cyber)",
                }}
              />
            </div>
          </div>
        </MetricCard>
        <MetricCard label="DESCUBRIMIENTOS PUBLICABLES" accent="var(--color-paper)" icon={<Sparkles size={16} />}>
          <AnimatedCounter value={publishable} />
        </MetricCard>
      </section>

      {/* Terminal + Chart */}
      <section className="grid gap-5 lg:grid-cols-2">
        <div>
          <h2 className="font-display text-sm tracking-widest mb-3 text-[color:var(--color-muted-foreground)]">
            ⬡ TERMINAL DE DESCUBRIMIENTOS
          </h2>
          <Terminal />
        </div>
        <div>
          <h2 className="font-display text-sm tracking-widest mb-3 text-[color:var(--color-muted-foreground)]">
            ⬡ EVOLUCIÓN DE FITNESS POR GENERACIÓN
          </h2>
          <div className="neon-frame">
            <div className="neon-inner p-4" style={{ height: "26rem" }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={FITNESS_EVOLUTION}>
                  <defs>
                    <linearGradient id="fit" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#7B68EE" stopOpacity={0.7} />
                      <stop offset="100%" stopColor="#7B68EE" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#7B68EE22" />
                  <XAxis dataKey="gen" stroke="#6b88a8" fontSize={11} tickLine={false} label={{ value: "Generación", position: "insideBottom", offset: -2, fill: "#6b88a8", fontSize: 10 }} />
                  <YAxis stroke="#6b88a8" fontSize={11} tickLine={false} domain={[0, 1]} />
                  <Tooltip
                    contentStyle={{
                      background: "#0D1B2A",
                      border: "1px solid #7B68EE55",
                      borderRadius: 8,
                      fontFamily: "JetBrains Mono",
                      fontSize: 12,
                    }}
                    labelStyle={{ color: "#00D4FF" }}
                  />
                  <Area
                    type="monotone"
                    dataKey="fitness"
                    stroke="#00D4FF"
                    strokeWidth={2.5}
                    fill="url(#fit)"
                    isAnimationActive
                    animationDuration={1600}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
