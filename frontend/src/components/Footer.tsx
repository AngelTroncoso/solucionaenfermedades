export function Footer() {
  return (
    <footer className="mt-16 border-t border-[color:var(--color-qwen)]/25 bg-[color:var(--color-surface)]/40 backdrop-blur">
      <div className="mx-auto max-w-7xl px-4 lg:px-6 py-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="space-y-1">
          <p className="font-display text-sm tracking-widest text-[color:var(--color-foreground)]">
            Built for <span className="text-[color:var(--color-qwen)]">Qwen</span> ×{" "}
            <span className="text-[color:var(--color-alibaba)]">Alibaba Cloud</span> Hackathon 2025
          </p>
          <p className="font-mono text-[11px] text-[color:var(--color-muted-foreground)]">
            Modelo: qwen3-235b-a22b · Provider: DashScope · Pipeline: Loop Engineering + Sakana FuGU
          </p>
        </div>
        <nav className="flex gap-4 font-mono text-[11px]">
          <a className="text-[color:var(--color-cyber)] hover:underline" href="https://github.com" target="_blank" rel="noreferrer">GitHub repo</a>
          <a className="text-[color:var(--color-cyber)] hover:underline" href="https://dashscope.console.aliyun.com" target="_blank" rel="noreferrer">DashScope</a>
          <a className="text-[color:var(--color-cyber)] hover:underline" href="https://huggingface.co/Qwen" target="_blank" rel="noreferrer">Qwen HuggingFace</a>
        </nav>
      </div>
    </footer>
  );
}
