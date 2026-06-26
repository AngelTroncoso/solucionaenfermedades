import { i as MOLECULES } from "./discoveries-C25peDSz.js";
import { jsx, jsxs } from "react/jsx-runtime";
import { motion } from "framer-motion";
//#region src/routes/matrix.tsx?tsr-split=component
function MolecularMatrix() {
	return /* @__PURE__ */ jsxs("div", {
		className: "space-y-8",
		children: [/* @__PURE__ */ jsxs("header", { children: [/* @__PURE__ */ jsx("h1", {
			className: "font-display text-3xl tracking-widest text-[color:var(--color-qwen)] glow-qwen",
			children: "MOLECULAR MATRIX"
		}), /* @__PURE__ */ jsx("p", {
			className: "font-mono text-xs text-[color:var(--color-muted-foreground)] mt-1",
			children: "Base de datos · 10 fármacos aprobados disponibles para reposicionamiento"
		})] }), /* @__PURE__ */ jsx("div", {
			className: "grid gap-6 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5",
			children: MOLECULES.map((m, i) => {
				const isGeneric = m.patent === "genérico";
				return /* @__PURE__ */ jsxs(motion.div, {
					initial: {
						opacity: 0,
						scale: .85
					},
					whileInView: {
						opacity: 1,
						scale: 1
					},
					viewport: { once: true },
					transition: {
						delay: i * .05,
						duration: .4
					},
					className: "group relative aspect-[1/1.05]",
					children: [
						/* @__PURE__ */ jsx("div", {
							className: "hex absolute inset-0 transition-all duration-300 group-hover:scale-105",
							style: {
								background: "linear-gradient(135deg, #7B68EE 0%, #00D4FF 50%, #FF6A00 100%)",
								filter: "drop-shadow(0 0 8px rgba(123,104,238,0.4))"
							}
						}),
						/* @__PURE__ */ jsxs("div", {
							className: "hex absolute inset-[2px] flex flex-col items-center justify-center p-3 text-center",
							style: { background: "var(--color-surface)" },
							children: [
								/* @__PURE__ */ jsx("div", {
									className: "font-display text-[13px] leading-tight text-[color:var(--color-foreground)]",
									children: m.name
								}),
								/* @__PURE__ */ jsx("div", {
									className: "mt-1 font-mono text-[10px] text-[color:var(--color-cyber)]",
									children: m.target
								}),
								/* @__PURE__ */ jsx("span", {
									className: "mt-2 px-1.5 py-0.5 rounded text-[9px] font-mono tracking-wider",
									style: {
										background: isGeneric ? "#00FF9F22" : "#ff3b6b22",
										color: isGeneric ? "#00FF9F" : "#ff6a6a",
										border: `1px solid ${isGeneric ? "#00FF9F66" : "#ff3b6b66"}`
									},
									children: isGeneric ? "GENÉRICO" : "VIGENTE"
								})
							]
						}),
						/* @__PURE__ */ jsx("div", {
							className: "pointer-events-none absolute left-1/2 -translate-x-1/2 top-full mt-2 w-56 opacity-0 group-hover:opacity-100 transition-opacity z-20",
							children: /* @__PURE__ */ jsxs("div", {
								className: "rounded border border-[color:var(--color-qwen)]/50 bg-black/90 p-2 font-mono text-[11px] text-[color:var(--color-foreground)]/90 shadow-xl",
								children: [/* @__PURE__ */ jsx("span", {
									className: "text-[color:var(--color-cyber)]",
									children: "[MoA] "
								}), m.moa]
							})
						})
					]
				}, m.name);
			})
		})]
	});
}
//#endregion
export { MolecularMatrix as component };
