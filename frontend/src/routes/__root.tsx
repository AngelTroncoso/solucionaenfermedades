import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  Link,
  createRootRouteWithContext,
  useRouter,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";
import { useEffect, type ReactNode } from "react";

import appCss from "../styles.css?url";
import { reportLovableError } from "../lib/lovable-error-reporting";
import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { ParticleBg } from "../components/ParticleBg";

function NotFoundComponent() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="font-display text-7xl text-[color:var(--color-qwen)] glow-qwen">404</h1>
        <h2 className="mt-4 font-display text-xl tracking-widest">Sector no encontrado</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          La ruta solicitada no existe en el sistema PharmaFuture.
        </p>
        <Link
          to="/"
          className="mt-6 inline-flex items-center justify-center rounded-md bg-[color:var(--color-qwen)] px-4 py-2 text-sm font-medium text-white hover:opacity-90"
        >
          Volver al Command Center
        </Link>
      </div>
    </div>
  );
}

function ErrorComponent({ error, reset }: { error: Error; reset: () => void }) {
  console.error(error);
  const router = useRouter();
  useEffect(() => {
    reportLovableError(error, { boundary: "tanstack_root_error_component" });
  }, [error]);
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="font-display text-xl tracking-widest">FALLO DEL SISTEMA</h1>
        <p className="mt-2 text-sm text-muted-foreground">El reactor cuántico necesita reiniciar.</p>
        <div className="mt-6 flex flex-wrap justify-center gap-2">
          <button
            onClick={() => { router.invalidate(); reset(); }}
            className="rounded-md bg-[color:var(--color-qwen)] px-4 py-2 text-sm text-white"
          >Reintentar</button>
          <a href="/" className="rounded-md border border-input px-4 py-2 text-sm">Inicio</a>
        </div>
      </div>
    </div>
  );
}

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "PharmaFuture 2050 — Drug Repurposing Discovery Engine" },
      { name: "description", content: "Visualización en tiempo real de descubrimientos de reposicionamiento farmacéutico. Powered by Qwen × Alibaba Cloud." },
      { name: "author", content: "PharmaFuture" },
      { property: "og:title", content: "PharmaFuture 2050" },
      { property: "og:description", content: "Drug repurposing discovery engine powered by Qwen × Alibaba Cloud." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Orbitron:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap",
      },
    ],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
});

function RootShell({ children }: { children: ReactNode }) {
  return (
    <html lang="es">
      <head><HeadContent /></head>
      <body>
        {children}
        <Scripts />
      </body>
    </html>
  );
}

function RootComponent() {
  const { queryClient } = Route.useRouteContext();
  return (
    <QueryClientProvider client={queryClient}>
      <div className="relative min-h-screen grid-bg">
        <ParticleBg />
        <Navbar />
        <main className="mx-auto max-w-7xl px-4 lg:px-6 py-8">
          <Outlet />
        </main>
        <Footer />
      </div>
    </QueryClientProvider>
  );
}
