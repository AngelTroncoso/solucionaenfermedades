import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { HeadContent, Link, Outlet, Scripts, createFileRoute, createRootRouteWithContext, createRouter, lazyRouteComponent, useRouter } from "@tanstack/react-router";
import { useEffect, useRef } from "react";
import { Hexagon } from "lucide-react";
import { jsx, jsxs } from "react/jsx-runtime";
//#region src/styles.css?url
var styles_default = "/assets/styles-DjsYlVUZ.css";
//#endregion
//#region src/lib/lovable-error-reporting.ts
function reportLovableError(error, context = {}) {
	if (typeof window === "undefined") return;
	window.__lovableEvents?.captureException?.(error, {
		source: "react_error_boundary",
		route: window.location.pathname,
		...context
	}, {
		mechanism: "react_error_boundary",
		handled: false,
		severity: "error"
	});
}
//#endregion
//#region src/components/Navbar.tsx
var links = [
	{
		to: "/",
		label: "COMMAND CENTER"
	},
	{
		to: "/discoveries",
		label: "DISCOVERIES"
	},
	{
		to: "/matrix",
		label: "MOLECULAR MATRIX"
	},
	{
		to: "/papers",
		label: "PAPERS"
	}
];
function Navbar() {
	return /* @__PURE__ */ jsxs("header", {
		className: "sticky top-0 z-40 backdrop-blur-xl bg-[color:var(--color-background)]/70 border-b border-[color:var(--color-qwen)]/30",
		children: [/* @__PURE__ */ jsx("div", { className: "absolute inset-x-0 -bottom-px h-px bg-gradient-to-r from-transparent via-[color:var(--color-cyber)] to-transparent opacity-70" }), /* @__PURE__ */ jsxs("div", {
			className: "mx-auto max-w-7xl px-4 lg:px-6 h-16 flex items-center justify-between gap-4",
			children: [
				/* @__PURE__ */ jsxs(Link, {
					to: "/",
					className: "flex items-center gap-2 font-display text-[color:var(--color-foreground)]",
					children: [/* @__PURE__ */ jsx(Hexagon, {
						className: "text-[color:var(--color-qwen)] glow-qwen",
						size: 22
					}), /* @__PURE__ */ jsx("span", {
						className: "tracking-widest text-sm sm:text-base",
						children: "PharmaFuture 2050"
					})]
				}),
				/* @__PURE__ */ jsx("nav", {
					className: "hidden md:flex items-center gap-1 font-mono text-[11px] tracking-widest",
					children: links.map((l) => /* @__PURE__ */ jsx(Link, {
						to: l.to,
						activeOptions: { exact: l.to === "/" },
						className: "px-3 py-2 rounded text-[color:var(--color-muted-foreground)] hover:text-[color:var(--color-cyber)] transition-colors",
						activeProps: { className: "px-3 py-2 rounded text-[color:var(--color-cyber)] bg-[color:var(--color-qwen)]/10" },
						children: l.label
					}, l.to))
				}),
				/* @__PURE__ */ jsx("div", {
					className: "hidden lg:block",
					children: /* @__PURE__ */ jsx("div", {
						className: "neon-frame",
						children: /* @__PURE__ */ jsxs("div", {
							className: "neon-inner px-3 py-1.5 font-mono text-[10px] tracking-widest text-[color:var(--color-foreground)] flex items-center gap-2",
							children: [
								/* @__PURE__ */ jsx(Hexagon, {
									size: 11,
									className: "text-[color:var(--color-qwen)]"
								}),
								/* @__PURE__ */ jsx("span", { children: "POWERED BY" }),
								/* @__PURE__ */ jsx("span", {
									className: "text-[color:var(--color-qwen)] font-semibold",
									children: "QWEN"
								}),
								/* @__PURE__ */ jsx("span", { children: "×" }),
								/* @__PURE__ */ jsx("span", {
									className: "text-[color:var(--color-alibaba)] font-semibold",
									children: "ALIBABA CLOUD"
								})
							]
						})
					})
				})
			]
		})]
	});
}
//#endregion
//#region src/components/Footer.tsx
function Footer() {
	return /* @__PURE__ */ jsx("footer", {
		className: "mt-16 border-t border-[color:var(--color-qwen)]/25 bg-[color:var(--color-surface)]/40 backdrop-blur",
		children: /* @__PURE__ */ jsxs("div", {
			className: "mx-auto max-w-7xl px-4 lg:px-6 py-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between",
			children: [/* @__PURE__ */ jsxs("div", {
				className: "space-y-1",
				children: [/* @__PURE__ */ jsxs("p", {
					className: "font-display text-sm tracking-widest text-[color:var(--color-foreground)]",
					children: [
						"Built for ",
						/* @__PURE__ */ jsx("span", {
							className: "text-[color:var(--color-qwen)]",
							children: "Qwen"
						}),
						" ×",
						" ",
						/* @__PURE__ */ jsx("span", {
							className: "text-[color:var(--color-alibaba)]",
							children: "Alibaba Cloud"
						}),
						" Hackathon 2025"
					]
				}), /* @__PURE__ */ jsx("p", {
					className: "font-mono text-[11px] text-[color:var(--color-muted-foreground)]",
					children: "Modelo: qwen3-235b-a22b · Provider: DashScope · Pipeline: Loop Engineering + Sakana FuGU"
				})]
			}), /* @__PURE__ */ jsxs("nav", {
				className: "flex gap-4 font-mono text-[11px]",
				children: [
					/* @__PURE__ */ jsx("a", {
						className: "text-[color:var(--color-cyber)] hover:underline",
						href: "https://github.com",
						target: "_blank",
						rel: "noreferrer",
						children: "GitHub repo"
					}),
					/* @__PURE__ */ jsx("a", {
						className: "text-[color:var(--color-cyber)] hover:underline",
						href: "https://dashscope.console.aliyun.com",
						target: "_blank",
						rel: "noreferrer",
						children: "DashScope"
					}),
					/* @__PURE__ */ jsx("a", {
						className: "text-[color:var(--color-cyber)] hover:underline",
						href: "https://huggingface.co/Qwen",
						target: "_blank",
						rel: "noreferrer",
						children: "Qwen HuggingFace"
					})
				]
			})]
		})
	});
}
//#endregion
//#region src/components/ParticleBg.tsx
function ParticleBg() {
	const ref = useRef(null);
	useEffect(() => {
		const canvas = ref.current;
		if (!canvas) return;
		const ctx = canvas.getContext("2d");
		let raf = 0;
		let w = canvas.width = window.innerWidth;
		let h = canvas.height = window.innerHeight;
		const N = Math.min(60, Math.floor(w * h / 28e3));
		const colors = [
			"#7B68EE",
			"#00D4FF",
			"#FF6A00"
		];
		const pts = Array.from({ length: N }, () => ({
			x: Math.random() * w,
			y: Math.random() * h,
			vx: (Math.random() - .5) * .25,
			vy: (Math.random() - .5) * .25,
			r: 1 + Math.random() * 1.8,
			c: colors[Math.floor(Math.random() * colors.length)]
		}));
		const onResize = () => {
			w = canvas.width = window.innerWidth;
			h = canvas.height = window.innerHeight;
		};
		window.addEventListener("resize", onResize);
		const loop = () => {
			ctx.clearRect(0, 0, w, h);
			for (const p of pts) {
				p.x += p.vx;
				p.y += p.vy;
				if (p.x < 0 || p.x > w) p.vx *= -1;
				if (p.y < 0 || p.y > h) p.vy *= -1;
				ctx.beginPath();
				ctx.fillStyle = p.c;
				ctx.globalAlpha = .55;
				ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
				ctx.fill();
			}
			ctx.globalAlpha = .08;
			for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) {
				const dx = pts[i].x - pts[j].x;
				const dy = pts[i].y - pts[j].y;
				if (dx * dx + dy * dy < 18e3) {
					ctx.strokeStyle = "#7B68EE";
					ctx.beginPath();
					ctx.moveTo(pts[i].x, pts[i].y);
					ctx.lineTo(pts[j].x, pts[j].y);
					ctx.stroke();
				}
			}
			raf = requestAnimationFrame(loop);
		};
		loop();
		return () => {
			cancelAnimationFrame(raf);
			window.removeEventListener("resize", onResize);
		};
	}, []);
	return /* @__PURE__ */ jsx("canvas", {
		ref,
		className: "pointer-events-none fixed inset-0 -z-10 opacity-60",
		"aria-hidden": true
	});
}
//#endregion
//#region src/routes/__root.tsx
function NotFoundComponent() {
	return /* @__PURE__ */ jsx("div", {
		className: "flex min-h-screen items-center justify-center bg-background px-4",
		children: /* @__PURE__ */ jsxs("div", {
			className: "max-w-md text-center",
			children: [
				/* @__PURE__ */ jsx("h1", {
					className: "font-display text-7xl text-[color:var(--color-qwen)] glow-qwen",
					children: "404"
				}),
				/* @__PURE__ */ jsx("h2", {
					className: "mt-4 font-display text-xl tracking-widest",
					children: "Sector no encontrado"
				}),
				/* @__PURE__ */ jsx("p", {
					className: "mt-2 text-sm text-muted-foreground",
					children: "La ruta solicitada no existe en el sistema PharmaFuture."
				}),
				/* @__PURE__ */ jsx(Link, {
					to: "/",
					className: "mt-6 inline-flex items-center justify-center rounded-md bg-[color:var(--color-qwen)] px-4 py-2 text-sm font-medium text-white hover:opacity-90",
					children: "Volver al Command Center"
				})
			]
		})
	});
}
function ErrorComponent({ error, reset }) {
	console.error(error);
	const router = useRouter();
	useEffect(() => {
		reportLovableError(error, { boundary: "tanstack_root_error_component" });
	}, [error]);
	return /* @__PURE__ */ jsx("div", {
		className: "flex min-h-screen items-center justify-center bg-background px-4",
		children: /* @__PURE__ */ jsxs("div", {
			className: "max-w-md text-center",
			children: [
				/* @__PURE__ */ jsx("h1", {
					className: "font-display text-xl tracking-widest",
					children: "FALLO DEL SISTEMA"
				}),
				/* @__PURE__ */ jsx("p", {
					className: "mt-2 text-sm text-muted-foreground",
					children: "El reactor cuántico necesita reiniciar."
				}),
				/* @__PURE__ */ jsxs("div", {
					className: "mt-6 flex flex-wrap justify-center gap-2",
					children: [/* @__PURE__ */ jsx("button", {
						onClick: () => {
							router.invalidate();
							reset();
						},
						className: "rounded-md bg-[color:var(--color-qwen)] px-4 py-2 text-sm text-white",
						children: "Reintentar"
					}), /* @__PURE__ */ jsx("a", {
						href: "/",
						className: "rounded-md border border-input px-4 py-2 text-sm",
						children: "Inicio"
					})]
				})
			]
		})
	});
}
var Route$4 = createRootRouteWithContext()({
	head: () => ({
		meta: [
			{ charSet: "utf-8" },
			{
				name: "viewport",
				content: "width=device-width, initial-scale=1"
			},
			{ title: "PharmaFuture 2050 — Drug Repurposing Discovery Engine" },
			{
				name: "description",
				content: "Visualización en tiempo real de descubrimientos de reposicionamiento farmacéutico. Powered by Qwen × Alibaba Cloud."
			},
			{
				name: "author",
				content: "PharmaFuture"
			},
			{
				property: "og:title",
				content: "PharmaFuture 2050"
			},
			{
				property: "og:description",
				content: "Drug repurposing discovery engine powered by Qwen × Alibaba Cloud."
			},
			{
				property: "og:type",
				content: "website"
			},
			{
				name: "twitter:card",
				content: "summary"
			}
		],
		links: [
			{
				rel: "stylesheet",
				href: styles_default
			},
			{
				rel: "preconnect",
				href: "https://fonts.googleapis.com"
			},
			{
				rel: "preconnect",
				href: "https://fonts.gstatic.com",
				crossOrigin: "anonymous"
			},
			{
				rel: "stylesheet",
				href: "https://fonts.googleapis.com/css2?family=Orbitron:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap"
			}
		]
	}),
	shellComponent: RootShell,
	component: RootComponent,
	notFoundComponent: NotFoundComponent,
	errorComponent: ErrorComponent
});
function RootShell({ children }) {
	return /* @__PURE__ */ jsxs("html", {
		lang: "es",
		children: [/* @__PURE__ */ jsx("head", { children: /* @__PURE__ */ jsx(HeadContent, {}) }), /* @__PURE__ */ jsxs("body", { children: [children, /* @__PURE__ */ jsx(Scripts, {})] })]
	});
}
function RootComponent() {
	const { queryClient } = Route$4.useRouteContext();
	return /* @__PURE__ */ jsx(QueryClientProvider, {
		client: queryClient,
		children: /* @__PURE__ */ jsxs("div", {
			className: "relative min-h-screen grid-bg",
			children: [
				/* @__PURE__ */ jsx(ParticleBg, {}),
				/* @__PURE__ */ jsx(Navbar, {}),
				/* @__PURE__ */ jsx("main", {
					className: "mx-auto max-w-7xl px-4 lg:px-6 py-8",
					children: /* @__PURE__ */ jsx(Outlet, {})
				}),
				/* @__PURE__ */ jsx(Footer, {})
			]
		})
	});
}
//#endregion
//#region src/routes/papers.tsx
var $$splitComponentImporter$3 = () => import("./papers-CG_Zdko2.js");
var Route$3 = createFileRoute("/papers")({
	head: () => ({ meta: [{ title: "Paper Generator — PharmaFuture 2050" }, {
		name: "description",
		content: "Generador automático de papers académicos para descubrimientos con fitness ≥ 0.80."
	}] }),
	component: lazyRouteComponent($$splitComponentImporter$3, "component")
});
//#endregion
//#region src/routes/matrix.tsx
var $$splitComponentImporter$2 = () => import("./matrix-yoT0RRgg.js");
var Route$2 = createFileRoute("/matrix")({
	head: () => ({ meta: [{ title: "Molecular Matrix — PharmaFuture 2050" }, {
		name: "description",
		content: "Base de datos de fármacos aprobados visualizada en grid hexagonal."
	}] }),
	component: lazyRouteComponent($$splitComponentImporter$2, "component")
});
//#endregion
//#region src/routes/discoveries.tsx
var $$splitComponentImporter$1 = () => import("./discoveries-DJ1md2_4.js");
var Route$1 = createFileRoute("/discoveries")({
	head: () => ({ meta: [{ title: "Discovery Feed — PharmaFuture 2050" }, {
		name: "description",
		content: "Timeline de descubrimientos farmacéuticos generados por agentes Qwen."
	}] }),
	component: lazyRouteComponent($$splitComponentImporter$1, "component")
});
//#endregion
//#region src/routes/index.tsx
var $$splitComponentImporter = () => import("./routes-B1TQZ3QU.js");
var Route = createFileRoute("/")({
	head: () => ({ meta: [{ title: "Command Center — PharmaFuture 2050" }, {
		name: "description",
		content: "Métricas en tiempo real del motor de descubrimiento farmacéutico Qwen × Alibaba Cloud."
	}] }),
	component: lazyRouteComponent($$splitComponentImporter, "component")
});
//#endregion
//#region src/routeTree.gen.ts
var PapersRoute = Route$3.update({
	id: "/papers",
	path: "/papers",
	getParentRoute: () => Route$4
});
var MatrixRoute = Route$2.update({
	id: "/matrix",
	path: "/matrix",
	getParentRoute: () => Route$4
});
var DiscoveriesRoute = Route$1.update({
	id: "/discoveries",
	path: "/discoveries",
	getParentRoute: () => Route$4
});
var rootRouteChildren = {
	IndexRoute: Route.update({
		id: "/",
		path: "/",
		getParentRoute: () => Route$4
	}),
	DiscoveriesRoute,
	MatrixRoute,
	PapersRoute
};
var routeTree = Route$4._addFileChildren(rootRouteChildren)._addFileTypes();
//#endregion
//#region src/router.tsx
var getRouter = () => {
	return createRouter({
		routeTree,
		context: { queryClient: new QueryClient() },
		scrollRestoration: true,
		defaultPreloadStaleTime: 0
	});
};
//#endregion
export { getRouter };
