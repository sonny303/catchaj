// Renders the Catchaj product guide and local quick-start experience.
// Presents the workflow, capabilities, installation paths, and support links.

import { createFileRoute, Link } from "@tanstack/react-router";
import logoAsset from "@/assets/catchaj-logo.png.asset.json";
import {
  ArrowDownRight,
  ArrowRight,
  Bot,
  Braces,
  Check,
  Code2,
  GitBranch,
  MapPin,
  Network,
  Search,
  Sparkles,
  Terminal,
  UserRoundCog,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  agentCapabilities,
  buildCapabilities,
  capabilities,
  installMethods,
  prerequisites,
  quickExample,
} from "@/data/catchaj";

export const Route = createFileRoute("/how-to")({
  head: () => ({
    meta: [
      { title: "How to use Catchaj — Product guide and setup" },
      {
        name: "description",
        content: "Learn how Catchaj searches, resolves context, installs locally, and extends across Node, Python, and Docker.",
      },
      { property: "og:title", content: "How to use Catchaj — Search wider. Build faster." },
      {
        property: "og:description",
        content: "A practical guide to Catchaj capabilities, local installation, first queries, plugins, and agent workflows.",
      },
      { property: "og:url", content: "/how-to" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [
      { rel: "canonical", href: "/how-to" },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Work+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap",
      },
    ],
  }),
  component: CatchajPage,
});

const capabilityIcons = [Search, UserRoundCog, MapPin, Network, Terminal] as const;

function CodeBlock({ lines, label }: { lines: readonly string[]; label: string }) {
  return (
    <div className="overflow-hidden rounded-md border border-border bg-ink text-paper">
      <div className="flex h-10 items-center justify-between border-b border-paper/15 px-4">
        <span className="font-mono text-[10px] uppercase text-paper-muted">{label}</span>
        <span className="status-dot" aria-hidden="true" />
      </div>
      <pre className="overflow-x-auto p-4 font-mono text-xs leading-7 sm:p-6">
        <code>{lines.map((line, index) => <span key={line} className="block whitespace-pre"><span className="select-none text-lime">{index + 1}  </span>{line}</span>)}</code>
      </pre>
    </div>
  );
}

function CatchajPage() {
  return (
    <main className="overflow-hidden bg-background text-foreground">
      <header className="border-b border-border">
        <div className="mx-auto flex min-h-20 max-w-7xl items-center justify-between gap-4 px-5 py-4 sm:px-8 lg:px-12">
          <Link to="/" aria-label="Catchaj home" className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
            <img src={logoAsset.url} alt="Catchaj" className="h-8 w-auto" />
          </Link>
          <nav aria-label="Primary navigation" className="hidden items-center gap-8 lg:flex">
            <Link to="/" className="nav-link">Why we built this</Link>
            <Link to="/how-to" className="nav-link text-foreground" aria-current="page">How to use</Link>
            <Link to="/clexibility" className="nav-link">Clexibility</Link>
          </nav>
          <Button asChild size="lg" className="min-h-11 shadow-none">
            <a href="#install">Install locally <ArrowDownRight aria-hidden="true" /></a>
          </Button>
        </div>
      </header>

      <section id="top" className="mx-auto grid max-w-7xl items-center gap-12 px-5 py-16 sm:px-8 lg:min-h-[46rem] lg:grid-cols-[0.92fr_1.08fr] lg:px-12 lg:py-24">
        <div className="max-w-2xl">
          <p className="eyebrow">Context-aware tools for modern teams</p>
          <h1 className="mt-7 font-editorial text-5xl leading-[0.96] sm:text-7xl lg:text-[5.5rem]">
            Search wider.<br />Resolve context.<br /><em className="text-accent">Build faster.</em>
          </h1>
          <p className="mt-8 max-w-xl text-lg leading-8 text-muted-foreground sm:text-xl">
            catchaj brings flexible search, dynamic role titles, and domain-aware locations into one plug-and-play toolkit. Use the CLI, import the library, or extend it with your own adapters.
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-5">
            <Button asChild size="lg" className="min-h-11 shadow-none"><a href="#install">Install locally <ArrowDownRight aria-hidden="true" /></a></Button>
            <a className="nav-link inline-flex min-h-11 items-center gap-2" href="#capabilities">Explore capabilities <ArrowRight className="h-4 w-4" aria-hidden="true" /></a>
          </div>
        </div>

        <div className="relative mx-auto w-full max-w-2xl" aria-label="catchaj command line search example">
          <div className="mb-3 flex items-center justify-between font-mono text-[10px] uppercase text-muted-foreground">
            <span>Live query / 001</span><span className="stamp-small">Ready</span>
          </div>
          <div className="overflow-hidden rounded-md border border-foreground bg-ink text-paper">
            <div className="flex h-12 items-center justify-between border-b border-paper/15 px-4">
              <div className="flex items-center gap-2"><Terminal className="h-4 w-4 text-lime" aria-hidden="true" /><span className="font-mono text-[10px] uppercase text-paper-muted">catchaj terminal</span></div>
              <span className="font-mono text-[10px] text-lime">PROCESS / COMPLETE</span>
            </div>
            <div className="p-5 font-mono text-xs leading-7 sm:p-8 sm:text-sm">
              <p className="overflow-x-auto whitespace-nowrap"><span className="text-lime">$</span> {quickExample.command}</p>
              <p className="mt-7 text-paper-muted">Searching configured domains...</p>
              <p className="mt-2"><span className="text-lime">✓</span> {quickExample.result}</p>
              <div className="mt-7 space-y-3 border-t border-paper/15 pt-6">
                {quickExample.rows.map((row, index) => (
                  <div key={row.source} className="grid grid-cols-[1.5rem_minmax(0,1fr)] gap-2">
                    <span className="text-lime">0{index + 1}</span><p><strong className="font-normal text-lime">{row.source}</strong><span className="text-paper-muted"> → {row.text}</span></p>
                  </div>
                ))}
              </div>
            </div>
          </div>
          <p className="mt-4 text-right font-mono text-[10px] uppercase text-muted-foreground">One query. Every relevant domain.</p>
        </div>
      </section>

      <section aria-label="Product principles" className="border-y border-border bg-card">
        <div className="mx-auto grid max-w-7xl divide-y divide-border px-5 sm:px-8 md:grid-cols-3 md:divide-x md:divide-y-0 lg:px-12">
          {["Plug in without rebuilding", "Learn from real usage", "Extend without limits"].map((item, index) => (
            <div key={item} className="grid grid-cols-[auto_1fr] gap-4 py-6 md:px-7 first:pl-0 last:pr-0">
              <span className="font-mono text-xs font-bold text-olive">0{index + 1}</span><p className="text-sm font-semibold">{item}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="capabilities" className="mx-auto max-w-7xl px-5 py-24 sm:px-8 lg:px-12 lg:py-32">
        <div className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr]">
          <div><p className="eyebrow">Features at a glance</p><h2 className="mt-5 text-4xl font-bold sm:text-6xl">Useful alone.<br /><em className="font-editorial font-medium text-olive">Stronger together.</em></h2></div>
          <p className="max-w-2xl self-end text-lg leading-8 text-muted-foreground">Start with a single command. Add search domains, title logic, location context, and custom adapters as your needs grow.</p>
        </div>
        <div className="mt-14 grid border-l border-t border-border sm:grid-cols-2 lg:grid-cols-3">
          {capabilities.map((item, index) => {
            const Icon = capabilityIcons[index] ?? Braces;
            return (
              <article key={item.number} className="min-h-64 border-b border-r border-border p-6 sm:p-8">
                <div className="flex items-start justify-between gap-4"><div className="icon-tile"><Icon aria-hidden="true" /></div><span className="font-mono text-[10px] uppercase text-muted-foreground">{item.marker}</span></div>
                <p className="mt-10 font-mono text-[10px] font-bold text-olive">{item.number}</p>
                <h3 className="mt-2 text-xl font-bold">{item.title}</h3><p className="mt-3 text-sm leading-6 text-muted-foreground">{item.text}</p>
              </article>
            );
          })}
          <article className="flex min-h-64 flex-col justify-between border-b border-r border-border bg-ink p-6 text-paper sm:p-8">
            <Sparkles className="h-5 w-5 text-lime" aria-hidden="true" /><div><p className="font-editorial text-2xl italic">Your system has its own context.</p><p className="mt-3 text-sm leading-6 text-paper-muted">catchaj is designed to meet it there.</p></div>
          </article>
        </div>
      </section>

      <section id="agents" className="border-y border-border bg-card py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-5 sm:px-8 lg:px-12">
          <p className="eyebrow">Intelligence that compounds</p>
          <div className="mt-6 grid gap-8 lg:grid-cols-2">
            <article className="rounded-md border border-border bg-background p-6 sm:p-10">
              <div className="icon-tile"><Bot aria-hidden="true" /></div><p className="mt-9 font-mono text-[10px] uppercase text-olive">Continuous learning agent</p>
              <h2 className="mt-3 text-3xl font-bold sm:text-4xl">Relevance that improves with use.</h2>
              <p className="mt-5 text-base leading-7 text-muted-foreground">With optional training enabled, catchaj studies usage patterns, suggests improvements, and updates ranking models without a manual tuning cycle.</p>
              <ul className="mt-8 space-y-4 border-t border-border pt-6">{agentCapabilities.map((item) => <li key={item} className="flex gap-3 text-sm"><Check className="mt-0.5 h-4 w-4 shrink-0 text-olive" aria-hidden="true" />{item}</li>)}</ul>
            </article>
            <article className="rounded-md border border-border bg-background p-6 sm:p-10">
              <div className="icon-tile"><Code2 aria-hidden="true" /></div><p className="mt-9 font-mono text-[10px] uppercase text-olive">Powered by Google Antigravity</p>
              <h2 className="mt-3 text-3xl font-bold sm:text-4xl">Agents that build with you.</h2>
              <p className="mt-5 text-base leading-7 text-muted-foreground">The agentic build system can generate, test, deploy, and refine working code—turning long implementation cycles into focused reviews.</p>
              <ul className="mt-8 space-y-4 border-t border-border pt-6">{buildCapabilities.map((item) => <li key={item} className="flex gap-3 text-sm"><Check className="mt-0.5 h-4 w-4 shrink-0 text-olive" aria-hidden="true" />{item}</li>)}</ul>
            </article>
          </div>
        </div>
      </section>

      <section id="install" className="mx-auto max-w-7xl px-5 py-24 sm:px-8 lg:px-12 lg:py-32">
        <div className="grid gap-12 lg:grid-cols-[0.72fr_1.28fr]">
          <div>
            <p className="eyebrow">Quick start</p><h2 className="mt-5 text-4xl font-bold sm:text-6xl">From clone to query<br /><em className="font-editorial font-medium text-olive">in minutes.</em></h2>
            <p className="mt-7 max-w-md text-lg leading-8 text-muted-foreground">Choose your runtime, install the package, and start searching across configured domains.</p>
            <div className="mt-10 border-y border-border">
              {prerequisites.map((item) => <div key={item.name} className="grid grid-cols-[5rem_1fr_auto] items-center gap-3 border-b border-border py-4 text-xs last:border-b-0"><strong className="font-mono">{item.name}</strong><span className="text-muted-foreground">{item.version}</span><span className="font-mono text-[9px] uppercase text-olive">{item.note}</span></div>)}
            </div>
          </div>
          <div className="space-y-4">
            <CodeBlock label="Pull the repository" lines={["git clone https://github.com/your-org/catchaj.git", "cd catchaj"]} />
            <div className="grid gap-4 md:grid-cols-2">
              {installMethods.map((method, index) => (
                <div key={method.id} className={index === 0 ? "md:col-span-2" : ""}>
                  <div className="mb-2 flex items-center justify-between"><h3 className="text-sm font-semibold">{method.number} / {method.title}</h3><span className="stamp-small">{method.label}</span></div>
                  <CodeBlock label={method.id} lines={method.commands} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="bg-ink text-paper">
        <div className="mx-auto grid max-w-7xl items-center gap-12 px-5 py-24 sm:px-8 lg:grid-cols-[1fr_auto] lg:px-12 lg:py-28">
          <div><p className="eyebrow text-lime">One command to begin</p><h2 className="mt-6 text-5xl font-bold leading-tight sm:text-7xl">Your context.<br /><em className="font-editorial font-medium text-lime">Now searchable.</em></h2><p className="mt-7 max-w-xl text-lg leading-8 text-paper-muted">Clone the repository, install locally, and shape catchaj around the way your team already works.</p></div>
          <Button asChild size="lg" className="w-fit min-h-11 bg-accent text-accent-foreground shadow-none hover:bg-accent/90"><a href="#install">Install locally <ArrowRight aria-hidden="true" /></a></Button>
        </div>
      </section>

      <footer id="help" className="border-t border-border bg-card">
        <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:px-12">
          <div className="grid gap-10 md:grid-cols-3">
            <div><img src={logoAsset.url} alt="Catchaj" className="h-8 w-auto" /><p className="mt-4 max-w-xs text-sm leading-6 text-muted-foreground">Flexible search, role resolution, and agent-powered building for context-aware teams.</p></div>
            <div><p className="font-mono text-[10px] font-bold uppercase text-muted-foreground">Contribute</p><div className="mt-4 space-y-3 text-sm"><p className="flex items-center gap-2"><GitBranch className="h-4 w-4 text-olive" aria-hidden="true" />Fork, branch, and open a pull request.</p><p className="flex items-center gap-2"><Braces className="h-4 w-4 text-olive" aria-hidden="true" />MIT licensed.</p></div></div>
            <div><p className="font-mono text-[10px] font-bold uppercase text-muted-foreground">Get help</p><div className="mt-4 flex flex-col items-start gap-3"><a className="nav-link" href="#install">Installation guide</a><span className="text-sm text-muted-foreground">Community: #catchaj</span><span className="text-sm text-muted-foreground">Issues and API docs in the repository</span></div></div>
          </div>
          <div className="mt-14 flex flex-col gap-4 border-t border-border pt-6 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between"><p>Built for teams that need better context, not more complexity.</p><a className="nav-link w-fit" href="#top">Back to top ↑</a></div>
        </div>
      </footer>
    </main>
  );
}