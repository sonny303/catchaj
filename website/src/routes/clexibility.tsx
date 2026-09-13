// Defines Catchaj's Clexibility philosophy as an immersive editorial experience.
// Presents the nine-letter principle in an accessible, animated accordion.

import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, Sparkles } from "lucide-react";

import catchajLogo from "@/assets/catchaj-logo.png";
import logoAsset from "@/assets/catchaj-logo.png.asset.json";
import { Button } from "@/components/ui/button";

const logoSrc = catchajLogo || logoAsset.url || "/catchaj-logo.png";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { clexibilityAspects, clexibilitySummary } from "@/data/catchaj";

export const Route = createFileRoute("/clexibility")({
  head: () => ({
    meta: [
      { title: "Clexibility — The Catchaj design philosophy" },
      { name: "description", content: "Clear, explainable, extensible: the philosophy guiding Catchaj search, decisions, learning, and auditability." },
      { property: "og:title", content: "Clexibility — How Catchaj is designed" },
      { property: "og:description", content: "Nine principles for building a transparent, adaptable, and human-readable system." },
      { property: "og:url", content: "/clexibility" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [
      { rel: "canonical", href: "/clexibility" },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
      { rel: "stylesheet", href: "https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Work+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap" },
    ],
  }),
  component: ClexibilityPage,
});

function ClexibilityPage() {
  return (
    <main className="overflow-hidden bg-background text-foreground">
      <header className="border-b border-border">
        <div className="mx-auto flex min-h-20 max-w-7xl items-center justify-between gap-4 px-5 py-4 sm:px-8 lg:px-12">
          <Link to="/" aria-label="Catchaj home" className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
            <img
              src={logoSrc}
              alt="Catchaj"
              className="h-8 w-auto"
              onError={(e) => {
                if (e.currentTarget.src !== window.location.origin + "/catchaj-logo.png") {
                  e.currentTarget.src = "/catchaj-logo.png";
                }
              }}
            />
          </Link>
          <nav aria-label="Primary navigation" className="hidden items-center gap-8 md:flex">
            <Link to="/" className="nav-link">Why we built this</Link>
            <Link to="/how-to" className="nav-link">How to use</Link>
            <Link to="/clexibility" className="nav-link text-foreground" aria-current="page">Clexibility</Link>
          </nav>
          <Button asChild variant="outline" size="sm" className="min-h-11 shadow-none">
            <Link to="/how-to">How it works <ArrowRight aria-hidden="true" /></Link>
          </Button>
        </div>
      </header>

      <section className="relative mx-auto flex min-h-[42rem] max-w-5xl flex-col items-center justify-center px-5 py-24 text-center sm:px-8 lg:py-32">
        <div className="absolute left-1/2 top-24 h-24 w-px bg-border path-draw" aria-hidden="true" />
        <p className="eyebrow mt-24 reveal-rise">Pronounced “{clexibilitySummary.pronunciation}”</p>
        <h1 className="mt-8 font-editorial text-7xl leading-none reveal-rise reveal-delay-1 sm:text-9xl">{clexibilitySummary.word}</h1>
        <p className="mt-8 max-w-2xl text-xl leading-9 text-muted-foreground reveal-rise reveal-delay-2 sm:text-2xl">
          Clear enough to understand. Expressive enough to explain. Extensible enough to evolve.
        </p>
        <div className="mt-10 inline-flex items-center gap-3 rounded-full border border-border bg-card px-5 py-3 reveal-rise reveal-delay-2">
          <Sparkles className="h-4 w-4 text-accent" aria-hidden="true" />
          <p className="text-sm font-semibold">Clear <span className="text-muted-foreground">+</span> Explainable <span className="text-muted-foreground">+</span> Extensible</p>
        </div>
      </section>

      <section className="bg-ink text-paper">
        <div className="mx-auto max-w-4xl px-5 py-24 sm:px-8 lg:py-32">
          <p className="eyebrow text-lime">A philosophy with consequences</p>
          <h2 className="mt-6 font-editorial text-5xl leading-tight sm:text-7xl">Complex systems should not ask people to <em className="text-lime">trust the fog.</em></h2>
          <div className="mt-12 grid gap-8 text-base leading-8 text-paper-muted md:grid-cols-2">
            <p>Catchaj makes search logic, role relationships, and learning signals legible. People can see why a result appeared and where a decision came from.</p>
            <p>New operators and domain rules can be added without breaking familiar behavior. The system grows, while its contracts remain understandable.</p>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-5 py-24 sm:px-8 lg:py-32">
        <div className="grid gap-10 lg:grid-cols-[0.7fr_1.3fr] lg:gap-20">
          <div>
            <p className="eyebrow">Nine letters, one system</p>
            <h2 className="mt-6 font-editorial text-5xl leading-tight sm:text-6xl">A principle you can <em className="text-accent">inspect.</em></h2>
            <p className="mt-6 text-base leading-7 text-muted-foreground">Each letter turns the philosophy into a practical standard for how Catchaj behaves.</p>
          </div>
          <Accordion type="single" collapsible defaultValue="C-0" className="w-full border-t border-border">
            {clexibilityAspects.map((aspect, index) => (
              <AccordionItem key={`${aspect.letter}-${aspect.title}`} value={`${aspect.letter}-${index}`} className="group border-b border-border">
                <AccordionTrigger className="min-h-20 py-4 text-left hover:no-underline">
                  <span className="grid grid-cols-[2.5rem_1fr] items-center gap-4">
                    <span className="flex h-10 w-10 items-center justify-center rounded-md border border-border bg-card font-mono text-xs font-bold text-accent transition-colors group-data-[state=open]:bg-accent group-data-[state=open]:text-accent-foreground">{aspect.letter}</span>
                    <span className="font-editorial text-2xl">{aspect.title}</span>
                  </span>
                </AccordionTrigger>
                <AccordionContent className="pb-6 pl-14"><p className="max-w-xl text-sm leading-7 text-muted-foreground">{aspect.text}</p></AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </section>

      <section className="border-y border-border bg-secondary">
        <div className="mx-auto max-w-4xl px-5 py-20 text-center sm:px-8">
          <p className="eyebrow">In a nutshell</p>
          <blockquote className="mt-6 font-editorial text-4xl leading-tight sm:text-6xl">“{clexibilitySummary.equation}.”</blockquote>
          <p className="mx-auto mt-7 max-w-2xl text-base leading-7 text-muted-foreground">{clexibilitySummary.nutshell}</p>
        </div>
      </section>

      <footer className="border-t border-border bg-card">
        <div className="mx-auto flex max-w-7xl flex-col gap-8 px-5 py-12 sm:px-8 md:flex-row md:items-center md:justify-between lg:px-12">
          <img
            src={logoSrc}
            alt="Catchaj"
            className="h-8 w-auto"
            onError={(e) => {
              if (e.currentTarget.src !== window.location.origin + "/catchaj-logo.png") {
                e.currentTarget.src = "/catchaj-logo.png";
              }
            }}
          />
          <p className="text-sm text-muted-foreground">Clear by design. Human by default.</p>
          <Link to="/how-to" className="nav-link inline-flex items-center gap-2">
            See it in practice <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </div>
      </footer>
    </main>
  );
}