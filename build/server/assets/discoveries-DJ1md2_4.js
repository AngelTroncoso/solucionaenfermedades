import { t as DISCOVERIES } from "./discoveries-C25peDSz.js";
import { useState } from "react";
import { ChevronDown, FileText, X } from "lucide-react";
import { jsx, jsxs } from "react/jsx-runtime";
import { AnimatePresence, motion } from "framer-motion";
//#region src/routes/discoveries.tsx?tsr-split=component
var STATUS_COLOR = {
	NUEVO: "#00D4FF",
	"EN REVISIÓN": "#FFD700",
	PUBLICABLE: "#00FF9F",
	ARCHIVADO: "#6b88a8"
};
function fitnessColor(f) {
	if (f >= .8) return "#00FF9F";
	if (f >= .7) return "#FFD700";
	return "#ff6a6a";
}
function DiscoveryCard({ d, onPaper }) {
	const [open, setOpen] = useState(false);
	return /* @__PURE__ */ jsx(motion.article, {
		initial: {
			opacity: 0,
			x: -16
		},
		whileInView: {
			opacity: 1,
			x: 0
		},
		viewport: { once: true },
		transition: { duration: .45 },
		className: "neon-frame",
		children: /* @__PURE__ */ jsxs("div", {
			className: "neon-inner p-5",
			children: [
				/* @__PURE__ */ jsxs("div", {
					className: "flex flex-wrap items-center gap-3 text-xs font-mono",
					children: [
						/* @__PURE__ */ jsx("span", {
							className: "text-[color:var(--color-muted-foreground)]",
							children: d.timestamp
						}),
						/* @__PURE__ */ jsx("span", {
							className: "px-2 py-0.5 rounded text-[10px] tracking-widest",
							style: {
								background: STATUS_COLOR[d.status] + "22",
								color: STATUS_COLOR[d.status],
								border: `1px solid ${STATUS_COLOR[d.status]}55`
							},
							children: d.status
						}),
						/* @__PURE__ */ jsx("span", {
							className: "ml-auto text-[color:var(--color-muted-foreground)]",
							children: d.area
						})
					]
				}),
				/* @__PURE__ */ jsx("h3", {
					className: "mt-3 font-display text-xl md:text-2xl tracking-wide text-[color:var(--color-foreground)]",
					children: d.drug
				}),
				/* @__PURE__ */ jsxs("p", {
					className: "text-sm text-[color:var(--color-cyber)] font-mono",
					children: ["→ ", d.disease]
				}),
				/* @__PURE__ */ jsxs("div", {
					className: "mt-4",
					children: [/* @__PURE__ */ jsxs("div", {
						className: "flex items-center justify-between text-[11px] font-mono mb-1.5",
						children: [/* @__PURE__ */ jsx("span", {
							className: "text-[color:var(--color-muted-foreground)]",
							children: "FITNESS SCORE"
						}), /* @__PURE__ */ jsxs("span", {
							style: { color: fitnessColor(d.fitness) },
							children: [d.fitness.toFixed(3), " / 1.000"]
						})]
					}), /* @__PURE__ */ jsx("div", {
						className: "h-2 rounded-full bg-black/50 overflow-hidden",
						children: /* @__PURE__ */ jsx(motion.div, {
							initial: { width: 0 },
							whileInView: { width: `${d.fitness * 100}%` },
							viewport: { once: true },
							transition: { duration: 1.2 },
							className: "h-full rounded-full",
							style: {
								background: `linear-gradient(90deg, #ff3b6b 0%, #FFD700 50%, ${fitnessColor(d.fitness)} 100%)`,
								boxShadow: `0 0 12px ${fitnessColor(d.fitness)}66`
							}
						})
					})]
				}),
				/* @__PURE__ */ jsxs("div", {
					className: "mt-4 flex flex-wrap gap-2",
					children: [/* @__PURE__ */ jsxs("button", {
						onClick: () => setOpen((v) => !v),
						className: "flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono bg-[color:var(--color-qwen)]/15 text-[color:var(--color-qwen)] hover:bg-[color:var(--color-qwen)]/25",
						children: [/* @__PURE__ */ jsx(ChevronDown, {
							size: 14,
							className: open ? "rotate-180 transition-transform" : "transition-transform"
						}), "Ver Mecanismo Molecular"]
					}), /* @__PURE__ */ jsxs("button", {
						disabled: !d.paper,
						onClick: () => onPaper(d),
						className: "flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono bg-[color:var(--color-paper)]/10 text-[color:var(--color-paper)] hover:bg-[color:var(--color-paper)]/25 disabled:opacity-30 disabled:cursor-not-allowed",
						children: [/* @__PURE__ */ jsx(FileText, { size: 14 }), "Evaluar para Paper"]
					})]
				}),
				/* @__PURE__ */ jsx(AnimatePresence, { children: open && /* @__PURE__ */ jsx(motion.div, {
					initial: {
						opacity: 0,
						height: 0
					},
					animate: {
						opacity: 1,
						height: "auto"
					},
					exit: {
						opacity: 0,
						height: 0
					},
					className: "overflow-hidden",
					children: /* @__PURE__ */ jsxs("div", {
						className: "mt-4 p-3 rounded border border-[color:var(--color-qwen)]/30 bg-black/30 font-mono text-xs text-[color:var(--color-foreground)]/90",
						children: [/* @__PURE__ */ jsx("div", {
							className: "text-[color:var(--color-cyber)] mb-1",
							children: "[MECANISMO MOLECULAR]"
						}), d.mechanism]
					})
				}) })
			]
		})
	});
}
function PaperModal({ d, onClose }) {
	return /* @__PURE__ */ jsx(motion.div, {
		initial: { opacity: 0 },
		animate: { opacity: 1 },
		exit: { opacity: 0 },
		className: "fixed inset-0 z-50 grid place-items-center bg-black/70 backdrop-blur-sm p-4",
		onClick: onClose,
		children: /* @__PURE__ */ jsx(motion.div, {
			initial: {
				scale: .92,
				y: 20
			},
			animate: {
				scale: 1,
				y: 0
			},
			exit: { scale: .95 },
			onClick: (e) => e.stopPropagation(),
			className: "neon-frame max-w-lg w-full",
			children: /* @__PURE__ */ jsxs("div", {
				className: "neon-inner p-6",
				children: [
					/* @__PURE__ */ jsxs("div", {
						className: "flex items-start justify-between gap-4",
						children: [/* @__PURE__ */ jsxs("div", { children: [
							/* @__PURE__ */ jsx("div", {
								className: "font-mono text-[10px] tracking-widest text-[color:var(--color-paper)]",
								children: "══ APTO PARA PUBLICACIÓN ACADÉMICA ══"
							}),
							/* @__PURE__ */ jsx("h3", {
								className: "mt-2 font-display text-lg text-[color:var(--color-foreground)]",
								children: d.drug
							}),
							/* @__PURE__ */ jsx("p", {
								className: "text-sm text-[color:var(--color-cyber)] font-mono",
								children: d.disease
							})
						] }), /* @__PURE__ */ jsx("button", {
							onClick: onClose,
							className: "text-[color:var(--color-muted-foreground)] hover:text-white",
							children: /* @__PURE__ */ jsx(X, { size: 18 })
						})]
					}),
					/* @__PURE__ */ jsxs("div", {
						className: "mt-4 space-y-2 font-mono text-xs",
						children: [
							/* @__PURE__ */ jsxs("div", { children: [/* @__PURE__ */ jsx("span", {
								className: "text-[color:var(--color-muted-foreground)]",
								children: "Journal sugerido: "
							}), /* @__PURE__ */ jsx("span", {
								className: "text-[color:var(--color-paper)]",
								children: d.journal
							})] }),
							/* @__PURE__ */ jsxs("div", { children: [/* @__PURE__ */ jsx("span", {
								className: "text-[color:var(--color-muted-foreground)]",
								children: "Fitness: "
							}), /* @__PURE__ */ jsx("span", {
								className: "text-[color:var(--color-discovery)]",
								children: d.fitness.toFixed(3)
							})] }),
							/* @__PURE__ */ jsxs("div", { children: [/* @__PURE__ */ jsx("span", {
								className: "text-[color:var(--color-muted-foreground)]",
								children: "Área: "
							}), d.area] }),
							/* @__PURE__ */ jsx("div", {
								className: "pt-2 text-[color:var(--color-foreground)]/85",
								children: d.mechanism
							})
						]
					}),
					/* @__PURE__ */ jsxs("div", {
						className: "mt-5 flex gap-2",
						children: [/* @__PURE__ */ jsx("button", {
							className: "flex-1 py-2 rounded text-xs font-mono bg-[color:var(--color-paper)] text-black hover:opacity-90",
							children: "Exportar a PDF"
						}), /* @__PURE__ */ jsx("button", {
							className: "flex-1 py-2 rounded text-xs font-mono border border-[color:var(--color-paper)]/60 text-[color:var(--color-paper)] hover:bg-[color:var(--color-paper)]/10",
							children: "Copiar BibTeX"
						})]
					})
				]
			})
		})
	});
}
function DiscoveryFeed() {
	const [paperDoc, setPaperDoc] = useState(null);
	return /* @__PURE__ */ jsxs("div", {
		className: "space-y-6",
		children: [
			/* @__PURE__ */ jsxs("header", { children: [/* @__PURE__ */ jsx("h1", {
				className: "font-display text-3xl tracking-widest text-[color:var(--color-qwen)] glow-qwen",
				children: "DISCOVERY FEED"
			}), /* @__PURE__ */ jsxs("p", {
				className: "font-mono text-xs text-[color:var(--color-muted-foreground)] mt-1",
				children: [
					"Timeline en tiempo real · ",
					DISCOVERIES.length,
					" descubrimientos registrados"
				]
			})] }),
			/* @__PURE__ */ jsx("div", {
				className: "space-y-4",
				children: DISCOVERIES.map((d) => /* @__PURE__ */ jsx(DiscoveryCard, {
					d,
					onPaper: setPaperDoc
				}, d.id))
			}),
			/* @__PURE__ */ jsx(AnimatePresence, { children: paperDoc && /* @__PURE__ */ jsx(PaperModal, {
				d: paperDoc,
				onClose: () => setPaperDoc(null)
			}) })
		]
	});
}
//#endregion
export { DiscoveryFeed as component };
