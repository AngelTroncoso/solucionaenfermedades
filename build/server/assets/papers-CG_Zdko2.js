import { r as JOURNALS, t as DISCOVERIES } from "./discoveries-C25peDSz.js";
import { Copy, Download } from "lucide-react";
import { jsx, jsxs } from "react/jsx-runtime";
import { motion } from "framer-motion";
//#region src/routes/papers.tsx?tsr-split=component
function suggestedTitle(drug, disease) {
	return `Repurposing ${drug} as a Combination Therapy for ${disease}: A Computational Discovery Framework`;
}
function abstractFor(drug, disease, mechanism, fitness) {
	return `We report the computational identification of ${drug} as a high-fitness repurposing candidate for ${disease} (fitness=${fitness.toFixed(3)}). Using an evolutionary loop powered by qwen3-235b-a22b on Alibaba Cloud DashScope, we screened a multi-agent hypothesis pool and converged on a mechanism of action involving ${mechanism.toLowerCase()}. The combination shows strong in-silico synergy and is proposed for early-phase clinical validation.`;
}
function PaperGenerator() {
	const eligible = DISCOVERIES.filter((d) => d.fitness >= .8);
	return /* @__PURE__ */ jsxs("div", {
		className: "space-y-8",
		children: [
			/* @__PURE__ */ jsxs("header", { children: [/* @__PURE__ */ jsx("h1", {
				className: "font-display text-3xl tracking-widest text-[color:var(--color-paper)]",
				style: { textShadow: "0 0 24px #FFD70055" },
				children: "PAPER GENERATOR"
			}), /* @__PURE__ */ jsxs("p", {
				className: "font-mono text-xs text-[color:var(--color-muted-foreground)] mt-1",
				children: [
					"Descubrimientos con fitness ≥ 0.80 · ",
					eligible.length,
					" candidatos aptos para publicación"
				]
			})] }),
			/* @__PURE__ */ jsx("section", {
				className: "neon-frame",
				children: /* @__PURE__ */ jsxs("div", {
					className: "neon-inner p-4",
					children: [/* @__PURE__ */ jsx("div", {
						className: "font-mono text-[10px] tracking-widest text-[color:var(--color-muted-foreground)] mb-3",
						children: "⬡ JOURNALS RECOMENDADOS"
					}), /* @__PURE__ */ jsx("div", {
						className: "flex flex-wrap gap-2",
						children: JOURNALS.map((j) => /* @__PURE__ */ jsxs("div", {
							className: "flex items-center gap-2 px-3 py-1.5 rounded-full bg-[color:var(--color-paper)]/10 border border-[color:var(--color-paper)]/40 font-mono text-xs",
							children: [/* @__PURE__ */ jsx("span", {
								className: "text-[color:var(--color-foreground)]",
								children: j.name
							}), /* @__PURE__ */ jsxs("span", {
								className: "text-[color:var(--color-paper)]",
								children: ["IF: ", j.impact]
							})]
						}, j.name))
					})]
				})
			}),
			/* @__PURE__ */ jsx("div", {
				className: "grid gap-6",
				children: eligible.map((d, i) => /* @__PURE__ */ jsx(motion.div, {
					initial: {
						opacity: 0,
						y: 12
					},
					animate: {
						opacity: 1,
						y: 0
					},
					transition: { delay: i * .1 },
					className: "neon-frame",
					children: /* @__PURE__ */ jsxs("div", {
						className: "neon-inner p-6",
						children: [
							/* @__PURE__ */ jsxs("div", {
								className: "flex items-center gap-2 font-mono text-[10px] tracking-widest text-[color:var(--color-paper)]",
								children: ["⬡ DRAFT MANUSCRIPT · FITNESS ", d.fitness.toFixed(3)]
							}),
							/* @__PURE__ */ jsx("h2", {
								className: "mt-3 font-display text-lg md:text-xl text-[color:var(--color-foreground)] leading-snug",
								children: suggestedTitle(d.drug, d.disease)
							}),
							/* @__PURE__ */ jsxs("div", {
								className: "mt-4",
								children: [/* @__PURE__ */ jsx("div", {
									className: "font-mono text-[10px] tracking-widest text-[color:var(--color-cyber)] mb-1",
									children: "ABSTRACT"
								}), /* @__PURE__ */ jsx("p", {
									className: "text-sm text-[color:var(--color-foreground)]/85 leading-relaxed",
									children: abstractFor(d.drug, d.disease, d.mechanism, d.fitness)
								})]
							}),
							/* @__PURE__ */ jsxs("div", {
								className: "mt-4 flex flex-wrap items-center gap-3 text-xs font-mono",
								children: [/* @__PURE__ */ jsx("span", {
									className: "text-[color:var(--color-muted-foreground)]",
									children: "Target journal:"
								}), /* @__PURE__ */ jsxs("span", {
									className: "px-2 py-1 rounded bg-[color:var(--color-paper)]/15 text-[color:var(--color-paper)] border border-[color:var(--color-paper)]/40",
									children: [
										d.journal,
										" · IF ",
										JOURNALS.find((j) => j.name === d.journal)?.impact ?? "—"
									]
								})]
							}),
							/* @__PURE__ */ jsxs("div", {
								className: "mt-5 flex flex-wrap gap-2",
								children: [/* @__PURE__ */ jsxs("button", {
									className: "flex items-center gap-1.5 px-3 py-2 rounded text-xs font-mono bg-[color:var(--color-paper)] text-black hover:opacity-90",
									children: [/* @__PURE__ */ jsx(Download, { size: 14 }), " Exportar a PDF"]
								}), /* @__PURE__ */ jsxs("button", {
									className: "flex items-center gap-1.5 px-3 py-2 rounded text-xs font-mono border border-[color:var(--color-cyber)]/60 text-[color:var(--color-cyber)] hover:bg-[color:var(--color-cyber)]/10",
									children: [/* @__PURE__ */ jsx(Copy, { size: 14 }), " Copiar BibTeX"]
								})]
							})
						]
					})
				}, d.id))
			})
		]
	});
}
//#endregion
export { PaperGenerator as component };
