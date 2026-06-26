import { n as FITNESS_EVOLUTION, t as DISCOVERIES } from "./discoveries-C25peDSz.js";
import { useEffect, useRef, useState } from "react";
import { Activity, FlaskConical, Pause, Play, Sparkles } from "lucide-react";
import { jsx, jsxs } from "react/jsx-runtime";
import { motion } from "framer-motion";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
//#region src/components/AnimatedCounter.tsx
function AnimatedCounter({ value, duration = 1400, decimals = 0, prefix = "", suffix = "" }) {
	const [n, setN] = useState(0);
	useEffect(() => {
		const start = performance.now();
		let raf = 0;
		const step = (t) => {
			const p = Math.min(1, (t - start) / duration);
			setN(value * (1 - Math.pow(1 - p, 3)));
			if (p < 1) raf = requestAnimationFrame(step);
		};
		raf = requestAnimationFrame(step);
		return () => cancelAnimationFrame(raf);
	}, [value, duration]);
	return /* @__PURE__ */ jsxs("span", { children: [
		prefix,
		n.toFixed(decimals),
		suffix
	] });
}
//#endregion
//#region src/components/Terminal.tsx
var CHANNEL_COLOR = {
	SISTEMA: "#888888",
	"QWEN-R": "#7B68EE",
	"QWEN-E": "#00D4FF",
	"QWEN-F": "#FF6A00",
	DISCOVERY: "#00FF9F",
	PAPER: "#FFD700"
};
function nowStamp() {
	const d = /* @__PURE__ */ new Date();
	const pad = (n) => n.toString().padStart(2, "0");
	return `2050.06.24 ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}
var SEQUENCES = [
	[
		{
			channel: "QWEN-R",
			text: "Analizando combinación: Montelukast + Dupilumab..."
		},
		{
			channel: "QWEN-E",
			text: "Fitness calculado: 0.847 — Umbral superado ✓"
		},
		{
			channel: "DISCOVERY",
			text: "════════════════════════════════════════"
		},
		{
			channel: "DISCOVERY",
			text: "★ NUEVO DESCUBRIMIENTO REGISTRADO ★"
		},
		{
			channel: "DISCOVERY",
			text: "Fármaco:     Montelukast + Dupilumab"
		},
		{
			channel: "DISCOVERY",
			text: "Enfermedad:  Rinitis Alérgica Crónica"
		},
		{
			channel: "DISCOVERY",
			text: "Mecanismo:   Bloqueo dual IL-4Rα + CYSLT1"
		},
		{
			channel: "DISCOVERY",
			text: "Fitness:     0.847 / 1.000"
		},
		{
			channel: "DISCOVERY",
			text: "Área médica: Inmunología / Alergología"
		},
		{
			channel: "PAPER",
			text: "══ APTO PARA PUBLICACIÓN ACADÉMICA ══"
		},
		{
			channel: "PAPER",
			text: "Journal sugerido: Nature Medicine (IF: 58.7)"
		},
		{
			channel: "PAPER",
			text: "Categoría: Drug Repurposing / Th2 Immunology"
		},
		{
			channel: "DISCOVERY",
			text: "════════════════════════════════════════"
		}
	],
	[
		{
			channel: "QWEN-F",
			text: "Generación 12: cruzando individuos top-5..."
		},
		{
			channel: "SISTEMA",
			text: "Pipeline Sakana FuGU activo — pool=128"
		},
		{
			channel: "QWEN-R",
			text: "Hipótesis: Omalizumab + Bilastina → Rinitis Perenne"
		},
		{
			channel: "QWEN-E",
			text: "Fitness: 0.823 — sinergia IgE/H1 confirmada"
		}
	],
	[
		{
			channel: "SISTEMA",
			text: "DashScope endpoint OK — qwen3-235b-a22b"
		},
		{
			channel: "QWEN-R",
			text: "Explorando espacio combinatorio: 45 pares activos"
		},
		{
			channel: "QWEN-E",
			text: "Fitness medio: 0.612  σ=0.09"
		}
	],
	[
		{
			channel: "QWEN-R",
			text: "Hipótesis: Ketotifeno + Rupatadina → Alergia D. Pteronyssinus"
		},
		{
			channel: "QWEN-E",
			text: "Fitness: 0.812 — mecanismo dual mastocito/PAF"
		},
		{
			channel: "PAPER",
			text: "Journal sugerido: Allergy (IF: 12.4)"
		}
	],
	[{
		channel: "QWEN-F",
		text: "Mutación aleatoria aplicada — diversidad +14%"
	}, {
		channel: "SISTEMA",
		text: "Checkpoint guardado: gen_012.pkl"
	}]
];
var TABS = [
	"ALL",
	"SISTEMA",
	"QWEN-R",
	"QWEN-E",
	"QWEN-F"
];
function Terminal({ height = "26rem" }) {
	const [lines, setLines] = useState([]);
	const [paused, setPaused] = useState(false);
	const [tab, setTab] = useState("ALL");
	const [flash, setFlash] = useState("");
	const idRef = useRef(0);
	const seqRef = useRef(0);
	const boxRef = useRef(null);
	useEffect(() => {
		if (paused) return;
		let cancelled = false;
		const emit = async () => {
			const seq = SEQUENCES[seqRef.current % SEQUENCES.length];
			seqRef.current++;
			for (const entry of seq) {
				if (cancelled || paused) return;
				idRef.current++;
				const line = {
					id: idRef.current,
					time: nowStamp(),
					channel: entry.channel,
					text: entry.text
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
	return /* @__PURE__ */ jsxs("div", {
		className: `relative rounded-xl border border-[color:var(--color-qwen)]/30 overflow-hidden ${flash === "discovery" ? "flash-discovery" : flash === "paper" ? "flash-paper" : ""}`,
		style: { background: "var(--color-terminal)" },
		children: [/* @__PURE__ */ jsxs("div", {
			className: "flex items-center justify-between px-3 py-2 border-b border-[color:var(--color-qwen)]/25 bg-black/40",
			children: [/* @__PURE__ */ jsx("div", {
				className: "flex gap-1",
				children: TABS.map((t) => /* @__PURE__ */ jsx("button", {
					onClick: () => setTab(t),
					className: `text-[11px] font-mono px-2 py-1 rounded transition-colors ${tab === t ? "bg-[color:var(--color-qwen)]/20 text-[color:var(--color-cyber)]" : "text-[color:var(--color-muted-foreground)] hover:text-[color:var(--color-foreground)]"}`,
					children: t
				}, t))
			}), /* @__PURE__ */ jsxs("button", {
				onClick: () => setPaused((p) => !p),
				className: "flex items-center gap-1.5 text-[11px] font-mono px-2.5 py-1 rounded bg-[color:var(--color-qwen)]/15 text-[color:var(--color-cyber)] hover:bg-[color:var(--color-qwen)]/30 transition-colors",
				children: [
					paused ? /* @__PURE__ */ jsx(Play, { size: 12 }) : /* @__PURE__ */ jsx(Pause, { size: 12 }),
					paused ? "REANUDAR" : "PAUSAR",
					" SIMULACIÓN"
				]
			})]
		}), /* @__PURE__ */ jsxs("div", {
			ref: boxRef,
			className: "scrollbar-thin overflow-y-auto px-3 py-2 font-mono text-[13px] leading-[1.55]",
			style: { height },
			children: [visible.map((l, i) => {
				const isLast = i === visible.length - 1;
				return /* @__PURE__ */ jsxs("div", {
					className: "whitespace-pre",
					children: [
						/* @__PURE__ */ jsx("span", {
							style: { color: "#3d6478" },
							children: `> ${l.time} `
						}),
						/* @__PURE__ */ jsxs("span", {
							style: { color: CHANNEL_COLOR[l.channel] },
							children: [
								"[",
								l.channel,
								"]"
							]
						}),
						/* @__PURE__ */ jsxs("span", {
							style: {
								color: CHANNEL_COLOR[l.channel],
								opacity: .92
							},
							children: [" ", l.text]
						}),
						isLast && /* @__PURE__ */ jsx("span", {
							className: "cursor-blink",
							style: { color: CHANNEL_COLOR[l.channel] },
							children: "▌"
						})
					]
				}, l.id);
			}), visible.length === 0 && /* @__PURE__ */ jsx("div", {
				className: "text-[color:var(--color-muted-foreground)]",
				children: "> Inicializando agentes Qwen..."
			})]
		})]
	});
}
//#endregion
//#region src/routes/index.tsx?tsr-split=component
function MetricCard({ label, children, accent, icon }) {
	return /* @__PURE__ */ jsx(motion.div, {
		initial: {
			opacity: 0,
			y: 16
		},
		animate: {
			opacity: 1,
			y: 0
		},
		transition: { duration: .6 },
		className: "neon-frame",
		children: /* @__PURE__ */ jsxs("div", {
			className: "neon-inner p-5",
			children: [/* @__PURE__ */ jsxs("div", {
				className: "flex items-center justify-between text-[11px] tracking-widest font-mono text-[color:var(--color-muted-foreground)]",
				children: [/* @__PURE__ */ jsx("span", { children: label }), /* @__PURE__ */ jsx("span", {
					style: { color: accent },
					children: icon
				})]
			}), /* @__PURE__ */ jsx("div", {
				className: "mt-3 font-display text-4xl lg:text-5xl",
				style: {
					color: accent,
					textShadow: `0 0 24px ${accent}55`
				},
				children
			})]
		})
	});
}
function CommandCenter() {
	const maxFitness = Math.max(...DISCOVERIES.map((d) => d.fitness));
	const publishable = DISCOVERIES.filter((d) => d.paper).length;
	return /* @__PURE__ */ jsxs("div", {
		className: "space-y-8",
		children: [
			/* @__PURE__ */ jsxs("section", {
				className: "text-center pt-4 pb-2",
				children: [
					/* @__PURE__ */ jsx(motion.h1, {
						initial: {
							opacity: 0,
							y: -10
						},
						animate: {
							opacity: 1,
							y: 0
						},
						className: "font-display text-4xl md:text-6xl tracking-[0.18em] text-[color:var(--color-qwen)] glow-qwen",
						children: "PHARMAFUTURE 2050"
					}),
					/* @__PURE__ */ jsxs("p", {
						className: "mt-3 font-mono text-xs md:text-sm tracking-[0.3em] text-[color:var(--color-muted-foreground)]",
						children: [
							"POWERED BY ",
							/* @__PURE__ */ jsx("span", {
								className: "text-[color:var(--color-qwen)]",
								children: "QWEN AI"
							}),
							" ×",
							" ",
							/* @__PURE__ */ jsx("span", {
								className: "text-[color:var(--color-alibaba)]",
								children: "ALIBABA CLOUD"
							})
						]
					}),
					/* @__PURE__ */ jsx("p", {
						className: "mt-2 font-mono text-[10px] text-[color:var(--color-muted-foreground)]/80",
						children: "Model: qwen3-235b-a22b · Infrastructure: Alibaba Cloud DashScope"
					})
				]
			}),
			/* @__PURE__ */ jsxs("section", {
				className: "grid gap-5 md:grid-cols-3",
				children: [
					/* @__PURE__ */ jsx(MetricCard, {
						label: "HIPÓTESIS ACTIVAS",
						accent: "var(--color-cyber)",
						icon: /* @__PURE__ */ jsx(Activity, { size: 16 }),
						children: /* @__PURE__ */ jsx(AnimatedCounter, { value: 1284 })
					}),
					/* @__PURE__ */ jsx(MetricCard, {
						label: "FITNESS MÁXIMO ALCANZADO",
						accent: "var(--color-qwen)",
						icon: /* @__PURE__ */ jsx(FlaskConical, { size: 16 }),
						children: /* @__PURE__ */ jsxs("div", { children: [/* @__PURE__ */ jsx(AnimatedCounter, {
							value: maxFitness,
							decimals: 3
						}), /* @__PURE__ */ jsx("div", {
							className: "mt-3 h-2 w-full rounded-full bg-black/50 overflow-hidden",
							children: /* @__PURE__ */ jsx(motion.div, {
								initial: { width: 0 },
								animate: { width: `${maxFitness * 100}%` },
								transition: {
									duration: 1.6,
									ease: "easeOut"
								},
								className: "h-full rounded-full",
								style: {
									background: "linear-gradient(90deg, var(--color-qwen), var(--color-cyber))",
									boxShadow: "0 0 16px var(--color-cyber)"
								}
							})
						})] })
					}),
					/* @__PURE__ */ jsx(MetricCard, {
						label: "DESCUBRIMIENTOS PUBLICABLES",
						accent: "var(--color-paper)",
						icon: /* @__PURE__ */ jsx(Sparkles, { size: 16 }),
						children: /* @__PURE__ */ jsx(AnimatedCounter, { value: publishable })
					})
				]
			}),
			/* @__PURE__ */ jsxs("section", {
				className: "grid gap-5 lg:grid-cols-2",
				children: [/* @__PURE__ */ jsxs("div", { children: [/* @__PURE__ */ jsx("h2", {
					className: "font-display text-sm tracking-widest mb-3 text-[color:var(--color-muted-foreground)]",
					children: "⬡ TERMINAL DE DESCUBRIMIENTOS"
				}), /* @__PURE__ */ jsx(Terminal, {})] }), /* @__PURE__ */ jsxs("div", { children: [/* @__PURE__ */ jsx("h2", {
					className: "font-display text-sm tracking-widest mb-3 text-[color:var(--color-muted-foreground)]",
					children: "⬡ EVOLUCIÓN DE FITNESS POR GENERACIÓN"
				}), /* @__PURE__ */ jsx("div", {
					className: "neon-frame",
					children: /* @__PURE__ */ jsx("div", {
						className: "neon-inner p-4",
						style: { height: "26rem" },
						children: /* @__PURE__ */ jsx(ResponsiveContainer, {
							width: "100%",
							height: "100%",
							children: /* @__PURE__ */ jsxs(AreaChart, {
								data: FITNESS_EVOLUTION,
								children: [
									/* @__PURE__ */ jsx("defs", { children: /* @__PURE__ */ jsxs("linearGradient", {
										id: "fit",
										x1: "0",
										y1: "0",
										x2: "0",
										y2: "1",
										children: [/* @__PURE__ */ jsx("stop", {
											offset: "0%",
											stopColor: "#7B68EE",
											stopOpacity: .7
										}), /* @__PURE__ */ jsx("stop", {
											offset: "100%",
											stopColor: "#7B68EE",
											stopOpacity: 0
										})]
									}) }),
									/* @__PURE__ */ jsx(CartesianGrid, {
										strokeDasharray: "3 3",
										stroke: "#7B68EE22"
									}),
									/* @__PURE__ */ jsx(XAxis, {
										dataKey: "gen",
										stroke: "#6b88a8",
										fontSize: 11,
										tickLine: false,
										label: {
											value: "Generación",
											position: "insideBottom",
											offset: -2,
											fill: "#6b88a8",
											fontSize: 10
										}
									}),
									/* @__PURE__ */ jsx(YAxis, {
										stroke: "#6b88a8",
										fontSize: 11,
										tickLine: false,
										domain: [0, 1]
									}),
									/* @__PURE__ */ jsx(Tooltip, {
										contentStyle: {
											background: "#0D1B2A",
											border: "1px solid #7B68EE55",
											borderRadius: 8,
											fontFamily: "JetBrains Mono",
											fontSize: 12
										},
										labelStyle: { color: "#00D4FF" }
									}),
									/* @__PURE__ */ jsx(Area, {
										type: "monotone",
										dataKey: "fitness",
										stroke: "#00D4FF",
										strokeWidth: 2.5,
										fill: "url(#fit)",
										isAnimationActive: true,
										animationDuration: 1600
									})
								]
							})
						})
					})
				})] })]
			})
		]
	});
}
//#endregion
export { CommandCenter as component };
