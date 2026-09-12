// Defines the approved editorial copy and interactive product story content.
// Keeps all Catchaj page data separate from the presentation layer.

export const helpers = [
  {
    number: "01",
    shortName: "Fact-Checker",
    name: "The Fact-Checker",
    role: "Builds one verified source of truth from your resume and interview notes.",
    rule: "If it isn’t in the Truth Document, it doesn’t belong in the answer.",
    output: "Verified candidate truth profile",
    marker: "FACTS / LOCKED",
  },
  {
    number: "02",
    shortName: "Job Scout",
    name: "The Job Scout",
    role: "Finds roles, removes repeats, and identifies the application platform.",
    rule: "Find the possibilities. Skip the repeats.",
    output: "Deduplicated opportunity stream",
    marker: "FOUND / SORTED",
  },
  {
    number: "03",
    shortName: "Strict Judge",
    name: "The Strict Judge",
    role: "Scores real fit, then applies non-negotiable location and friction rules.",
    rule: "85+ for direct forms. 95+ when another account gets in the way.",
    output: "Shortlist, decision log, and alert",
    marker: "FIT / CHECKED",
  },
  {
    number: "04",
    shortName: "Essay Drafter",
    name: "The Essay Drafter",
    role: "Writes concise answers using only experiences you can defend in an interview.",
    rule: "Specific beats impressive-sounding.",
    output: "Ready-to-review tailored answers",
    marker: "DRAFT / GROUNDED",
  },
  {
    number: "05",
    shortName: "Browser Copilot",
    name: "The Browser Copilot",
    role: "Fills fields, attaches your resume, and stages the live application.",
    rule: "The last click belongs to you.",
    output: "Pre-filled browser and human handoff",
    marker: "STAGED / WAITING",
  },
  {
    number: "06",
    shortName: "Privacy Guard",
    name: "The Privacy Guard",
    role: "Stops personal details, credentials, and secrets from leaking into public work.",
    rule: "Keep personal things personal.",
    output: "Protected credentials and zero-leak sandbox",
    marker: "PRIVATE / SAFE",
  },
] as const;

export const principles = [
  { number: "01", title: "Facts over fiction", text: "Strict grounding. Zero invented experience." },
  { number: "02", title: "Fit over volume", text: "High thresholds. Deliberate filters." },
  { number: "03", title: "Assistance over autopilot", text: "Human judgment at the finish line." },
] as const;

export const productChoices = [
  { number: "01", title: "Focus", text: "Optimize for fit, not application count." },
  { number: "02", title: "Trust", text: "Ground the draft, keep the review." },
  { number: "03", title: "Control", text: "Automate the prep, keep the decision." },
] as const;

export const stack = ["Python", "Google Gemini", "Playwright", "JobSpy", "Google Sheets", "Human judgment"] as const;
export const capabilities = [
  {
    number: "01",
    title: "Broadening search",
    text: "Move beyond exact matches with fuzzy, semantic, and multi-domain queries that understand intent.",
    marker: "QUERY / EXPANDED",
  },
  {
    number: "02",
    title: "Role titles",
    text: "Assign and resolve dynamic titles for people and services without forcing one rigid taxonomy.",
    marker: "ROLES / RESOLVED",
  },
  {
    number: "03",
    title: "Domain locations",
    text: "Map entities to the geographic or logical domains where they actually belong.",
    marker: "CONTEXT / MAPPED",
  },
  {
    number: "04",
    title: "Plugin system",
    text: "Add custom adapters in a few lines and extend the system without rebuilding its core.",
    marker: "PLUGINS / READY",
  },
  {
    number: "05",
    title: "CLI and library",
    text: "Run catchaj from the command line or import it directly into Node and Python projects.",
    marker: "TOOLS / FLEXIBLE",
  },
] as const;

export const agentCapabilities = [
  "Captures query successes and failures in real time",
  "Self-tunes ranking as usage patterns change",
  "Connects custom ML models through the Antigravity SDK",
  "Surfaces learning metrics in a focused dashboard",
] as const;

export const buildCapabilities = [
  "Create data pipelines, interfaces, and API endpoints",
  "Run continuous integration tests without manual handoffs",
  "Optimize performance from real-world usage signals",
  "Add custom skills through the Antigravity SDK",
] as const;

export const prerequisites = [
  { name: "git", version: "2.40 or newer", note: "Required" },
  { name: "node", version: "18 or newer", note: "Required" },
  { name: "python", version: "3.10 or newer", note: "Optional bindings" },
  { name: "Docker", version: "Current", note: "Optional sandbox" },
] as const;

export const installMethods = [
  {
    id: "node",
    number: "01",
    title: "Node / JavaScript",
    label: "Recommended",
    commands: ["npm ci", "npm run build", "npm link", "catchaj --help"],
  },
  {
    id: "python",
    number: "02",
    title: "Python bindings",
    label: "Optional",
    commands: ["python -m venv .venv", "source .venv/bin/activate", "pip install -e .[python]"],
  },
  {
    id: "docker",
    number: "03",
    title: "Docker sandbox",
    label: "Isolated",
    commands: ["docker build -t catchaj .", "docker run --rm -it catchaj --help"],
  },
] as const;

export const quickExample = {
  command: 'catchaj search "customer churn" --domains sales,support',
  result: "Found 12 results across 3 domains",
  rows: [
    { source: "sales-db", text: "Potential churn risk for account 1234" },
    { source: "support-logs", text: "Ticket #5678: churn discussion" },
  ],
} as const;

export const clexibilitySummary = {
  word: "Clexibility",
  pronunciation: "clee-ks-i-b-i-li-ty",
  equation: "Clear + Explainable + Extensible",
  nutshell:
    "The design principle that lets Catch‑a‑J turn complex, fuzzy search and role‑management problems into transparent, maintainable, and continuously improving solutions.",
} as const;

export const clexibilityAspects = [
  {
    letter: "C",
    title: "Clarity",
    text: "APIs, search queries, and role definitions are written in a human-readable, self-documenting style, so developers can instantly understand what a piece of code does.",
  },
  {
    letter: "L",
    title: "Linkability",
    text: "Entities (search results, roles, domains) are linked together through explicit identifiers, making relationships obvious and navigation simple.",
  },
  {
    letter: "E",
    title: "Extensibility",
    text: "The system is built around a plug-in architecture; new search operators, role-resolution strategies, or domain-mapping rules can be added without breaking existing functionality.",
  },
  {
    letter: "X",
    title: "Explainability",
    text: "The continuous-learning agent captures usage patterns and can produce 'why this result?' explanations, turning opaque ML-driven ranking into something you can audit.",
  },
  {
    letter: "I",
    title: "Interoperability",
    text: "Both CLI and library interfaces expose the same clear contracts, letting you use Catch‑a‑J from JavaScript, Python, or any language that can call the REST API.",
  },
  {
    letter: "B",
    title: "Behavioral Consistency",
    text: "Declarative configuration (e.g., role-title mappings) ensures that the same logic is applied everywhere, reducing bugs caused by ad-hoc code.",
  },
  {
    letter: "I",
    title: "Intuitiveness",
    text: "Default conventions follow familiar patterns (semantic search, role-based access), so new team members can start using it with minimal onboarding.",
  },
  {
    letter: "T",
    title: "Transparency",
    text: "Every change—whether from a human contributor or the autonomous learning agent—is logged and versioned, giving a clear audit trail.",
  },
  {
    letter: "Y",
    title: "Yield",
    text: "Because the system is both clear and extensible, you get higher productivity and faster delivery of new features.",
  },
] as const;