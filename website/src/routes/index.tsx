// Renders Catchaj's human-centered origin story and product principles.
// Connects the job-search problem to the practical guide and Clexibility philosophy.

import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowDownRight, ArrowRight, Check, Pause, ShieldCheck } from "lucide-react";

import catchajLogo from "@/assets/catchaj-logo.png";
import logoAsset from "@/assets/catchaj-logo.png.asset.json";
import { Button } from "@/components/ui/button";
import { helpers, principles, productChoices } from "@/data/catchaj";

const logoSrc = catchajLogo || logoAsset.url || "/catchaj-logo.png";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Catchaj — Human-first job application copilot" },
      { name: "description", content: "Why Catchaj exists: to remove repetitive job-search work while keeping truth, fit, and the final decision human." },
      { property: "og:title", content: "Catchaj — Your next chapter. Less of the copy-paste." },
      { property: "og:description", content: "A focused AI crew that finds, filters, drafts, and stages job applications—then pauses for your review." },
      { property: "og:url", content: "/" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [
      { rel: "canonical", href: "/" },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
      { rel: "stylesheet", href: "https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Work+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap" },
    ],
  }),
  component: CatchajStoryPage,
});

function SiteHeader() {
  return (
    <header className="border-b border-border bg-background">
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
          <Link to="/" className="nav-link text-foreground" aria-current="page">Why we built this</Link>
          <Link to="/how-to" className="nav-link">How to use</Link>
          <Link to="/clexibility" className="nav-link">Clexibility</Link>
        </nav>
        <Button asChild size="sm" className="min-h-11 shadow-none">
          <Link to="/how-to">How it works <ArrowRight aria-hidden="true" /></Link>
        </Button>
      </div>
    </header>
  );
}

function CatchajStoryPage() {
  return (
    <main className="overflow-hidden bg-background text-foreground">
      <SiteHeader />

      <section className="mx-auto grid max-w-7xl items-center gap-16 px-5 py-20 sm:px-8 lg:min-h-[48rem] lg:grid-cols-[0.9fr_1.1fr] lg:px-12 lg:py-24">
        <div className="max-w-2xl reveal-rise">
          <p className="eyebrow">A product experiment in human + AI</p>
          <h1 className="mt-8 font-editorial text-6xl leading-[0.92] sm:text-8xl lg:text-[6.5rem]">
            Your next chapter.<br /><em className="text-accent">Less of the copy-paste.</em>
          </h1>
          <p className="mt-8 max-w-xl text-lg leading-8 text-muted-foreground sm:text-xl">
            Job hunting is a full-time job. Catchaj takes on the repetitive search, filtering, drafting, and form-filling. <strong className="font-semibold text-foreground">You make the call.</strong>
          </p>
          <div className="mt-10 flex flex-wrap gap-4">
            <Button asChild size="lg" className="min-h-11 shadow-none"><Link to="/how-to">See how it works <ArrowRight aria-hidden="true" /></Link></Button>
            <Button asChild variant="outline" size="lg" className="min-h-11 shadow-none"><Link to="/clexibility">Read the philosophy</Link></Button>
          </div>
        </div>

        <div className="relative mx-auto w-full max-w-2xl py-10 reveal-rise reveal-delay-1" aria-label="A verified career truth becoming a staged application">
          <div className="truth-card relative z-10 w-[78%] -rotate-2 sm:w-[64%]">
            <div className="flex items-center justify-between border-b border-border pb-4"><span className="font-mono text-[10px] font-bold uppercase">Career truth / 001</span><span className="stamp-small">Verified</span></div>
            <h2 className="mt-6 text-xl font-semibold">Alex Morgan</h2><p className="mt-1 font-mono text-xs text-muted-foreground">Senior healthtech product leader</p>
            <div className="mt-7 space-y-4">{["12 years building clinical tools", "Led FHIR integrations", "Enterprise B2B SaaS"].map((fact) => <div key={fact} className="flex items-center gap-3 border-b border-border pb-3 text-sm"><Check className="h-4 w-4 shrink-0 text-accent" aria-hidden="true" />{fact}</div>)}</div>
          </div>
          <ArrowRight className="absolute left-[48%] top-[44%] z-20 h-4 w-4 text-accent" aria-hidden="true" />
          <div className="application-card relative -mt-7 ml-auto w-[82%] rotate-1 sm:-mt-28 sm:w-[68%]">
            <div className="flex items-start justify-between gap-3"><div><p className="font-mono text-[10px] uppercase text-muted-foreground">Beacon Health</p><h2 className="mt-2 text-lg font-semibold">Lead Product Manager</h2></div><span className="score-mark">92</span></div>
            <div className="mt-6 grid grid-cols-2 gap-2 font-mono text-[9px] uppercase">{["Location", "Experience", "Truth check", "Direct form"].map((item) => <span key={item} className="check-pill"><Check aria-hidden="true" />{item}</span>)}</div>
            <div className="mt-7 border-t border-dashed border-border pt-5 text-center"><p className="font-editorial text-xl italic">Your turn, human.</p><p className="mt-1 font-mono text-[9px] uppercase text-muted-foreground">Review · Make it yours · Submit</p></div>
          </div>
        </div>
      </section>

      <section aria-label="Guiding principles" className="border-y border-border bg-card">
        <div className="mx-auto grid max-w-7xl divide-y divide-border px-5 sm:px-8 md:grid-cols-3 md:divide-x md:divide-y-0 lg:px-12">
          {principles.map((item) => <article key={item.number} className="grid grid-cols-[auto_1fr] gap-4 py-7 md:px-7 first:pl-0 last:pr-0"><span className="font-mono text-xs font-bold text-accent">{item.number}</span><div><h2 className="text-sm font-semibold">{item.title}</h2><p className="mt-1 text-xs text-muted-foreground">{item.text}</p></div></article>)}
        </div>
      </section>

      <section className="mx-auto max-w-4xl px-5 py-24 sm:px-8 lg:py-32">
        <p className="eyebrow">The problem worth solving</p>
        <h2 className="mt-6 font-editorial text-5xl leading-tight sm:text-7xl">Great candidates.<br /><em className="text-accent">Endless busywork.</em></h2>
        <div className="mt-10 grid gap-8 text-lg leading-8 text-muted-foreground md:grid-cols-2">
          <p>The hard part should be finding the right next move—not typing your work history for the forty-seventh time into an antiquated application portal.</p>
          <p>Catchaj focuses on the few roles that genuinely fit. It uses your verified facts, rejects weak matches, and preserves your judgment at every consequential step.</p>
        </div>
      </section>

      <section className="border-y border-border bg-card py-24 lg:py-32">
        <div className="mx-auto max-w-5xl px-5 sm:px-8">
          <div className="max-w-2xl"><p className="eyebrow">A focused crew</p><h2 className="mt-6 font-editorial text-5xl leading-tight sm:text-7xl">Six helpers.<br /><em className="text-accent">One human decision.</em></h2></div>
          <ol className="mt-14 border-t border-border">
            {helpers.map((helper) => <li key={helper.number} className="grid gap-3 border-b border-border py-6 sm:grid-cols-[4rem_12rem_1fr]"><span className="font-mono text-xs text-accent">{helper.number}</span><h3 className="font-semibold">{helper.shortName}</h3><p className="text-sm leading-6 text-muted-foreground">{helper.role}</p></li>)}
          </ol>
          <Button asChild variant="outline" className="mt-10 min-h-11 shadow-none"><Link to="/how-to">Explore the full workflow <ArrowRight aria-hidden="true" /></Link></Button>
        </div>
      </section>

      <section className="bg-ink text-paper">
        <div className="mx-auto grid max-w-7xl items-center gap-14 px-5 py-24 sm:px-8 lg:grid-cols-[1.15fr_0.85fr] lg:px-12 lg:py-32">
          <div><p className="eyebrow text-lime">The most important feature is a pause</p><h2 className="mt-6 font-editorial text-6xl leading-[1] sm:text-8xl">It gets you to the button.<br /><em className="text-lime">You decide to press it.</em></h2><p className="mt-8 max-w-2xl text-lg leading-8 text-paper-muted">The form is filled, the resume attached, and the answer drafted. Then Catchaj stops. You review, edit, and keep the final say.</p></div>
          <div className="pause-stamp" aria-label="Human in the loop pause stamp"><Pause aria-hidden="true" /><span>Human in<br />the loop</span><small>Review before submit</small></div>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-5 py-24 sm:px-8 lg:py-32">
        <p className="eyebrow">The choices are the product</p><h2 className="mt-6 font-editorial text-5xl sm:text-7xl">Constraints, <em className="text-accent">on purpose.</em></h2>
        <div className="mt-14 grid border-y border-border md:grid-cols-3 md:divide-x md:divide-border">{productChoices.map((choice) => <article key={choice.number} className="border-b border-border py-8 last:border-b-0 md:border-b-0 md:px-8 first:pl-0 last:pr-0"><span className="font-mono text-xs text-accent">{choice.number}</span><h3 className="mt-7 text-xl font-semibold">{choice.title}</h3><p className="mt-3 text-sm leading-6 text-muted-foreground">{choice.text}</p></article>)}</div>
        <div className="mt-14 flex items-start gap-4 border-l-2 border-accent pl-5"><ShieldCheck className="mt-1 h-5 w-5 shrink-0 text-accent" aria-hidden="true" /><div><h3 className="font-semibold">Keep personal things personal.</h3><p className="mt-2 max-w-xl text-sm leading-6 text-muted-foreground">Local checks protect personal details and credentials. Demonstrations use a synthetic profile.</p></div></div>
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
          <div className="flex flex-wrap gap-6">
            <Link to="/how-to" className="nav-link">How to use</Link>
            <Link to="/clexibility" className="nav-link">Clexibility</Link>
          </div>
          <Link to="/how-to" className="nav-link inline-flex items-center gap-2">
            Start with the guide <ArrowDownRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </div>
      </footer>
    </main>
  );
}
