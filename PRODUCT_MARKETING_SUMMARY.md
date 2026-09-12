# Catchaj (`catchaj.`) — Product Marketing Summary & Web Design Handoff Brief

> **Document Type:** Product Marketing & Creative Brief for Website Design  
> **Target Recipient:** Web Designer / Creative Director / Frontend Experience Designer  
> **Product Name:** Catchaj (`catchaj.`)  
> **Core Category:** Human-in-the-Loop (HITL) AI Job Search Engine & Application Copilot  
> **Primary Tagline:** *"Your next chapter. Less of the copy-paste."*  
> **Supporting Tagline:** *"Built with AI. Designed around a human."*  
> **Core Philosophy:** *"The most important feature is a pause."*

---

## 1. Executive Summary & Product Vision

### 1.1 What is Catchaj?
**Catchaj** is an intelligent, agentic job application copilot built for high-caliber professionals who want leverage without sacrificing integrity. Instead of mass-spamming hundreds of job boards with low-quality AI generic fluff, Catchaj assembles a coordinated "crew" of six focused helpers to handle the soul-crushing administrative busywork: discovering roles, evaluating genuine alignment, drafting authentic application answers, and pre-filling ATS web forms in a real browser.

### 1.2 The Core Thesis: Anti-Spam, Pro-Human AI
The modern job hunt has devolved into a broken arms race:
- **The Spray-and-Pray Epidemic:** Candidates use blunt bot tools to blast out 500 applications a week.
- **The Recruiter Backlash:** Applicant Tracking Systems (ATS) install heavier filters and account gates to discard automated spam.
- **The Hallucination Danger:** Mainstream GenAI tools fabricate career metrics, inject generic corporate buzzwords (*"spearheaded synergies"*, *"leveraged cutting-edge paradigms"*), and actively damage candidate reputations.

**Catchaj flips this paradigm:**
1. **Facts Over Fiction:** Every draft is strictly grounded in a verified, candidate-owned **Career Truth Document**. If an accomplishment isn't true and documented, the AI is blocked from saying it.
2. **Fit Over Volume:** Rigorous gatekeeping. Roles are scored 0–100 against strict criteria. Location mismatches are rejected immediately, even with a 100/100 score. Account-gated applications (Workday, Taleo) raise the required threshold to 95+.
3. **Assistance Over Autopilot:** The system prepares everything—including launching a visible browser session and filling out the application form—but **it strictly never clicks submit**. The final handoff belongs to the human.

---

## 2. Target Audiences & User Personas

### 2.1 Primary User: The Intentional Senior Professional
- **Archetype:** Senior, Staff, or Lead Knowledge Worker (initial wedge: *Senior Healthcare / HealthTech Product Manager*).
- **Profile:** 8–15+ years of experience, high domain specificity (e.g., clinical integrations, FHIR/HL7, regulatory compliance, enterprise B2B SaaS).
- **Frustration:** Spending 45–60 minutes per application re-typing work history, wrestling with clunky ATS logins, and adapting resumes to arbitrary text fields.
- **Fear:** Being perceived as an "AI spammer" or having a model hallucinate experience they can't defend in an interview.
- **Desire:** High-touch, curated applications for 5–10 stellar opportunities, not 500 mediocre ones.

### 2.2 Secondary Audience: Hiring Managers, Tech Peers & Portfolio Evaluators
- **Profile:** Product leaders, design critics, engineering managers, and venture evaluators looking at Catchaj as an AI product case study.
- **What they look for:** Product taste, intentional constraints, sensible ethical boundaries, security/privacy hygiene, and genuine UX craftsmanship.

---

## 3. Brand Positioning, Voice & Aesthetic Direction

### 3.1 Positioning Statement
> *For experienced professionals navigating their next career chapter, **Catchaj** is the AI-assisted application partner that does the heavy lifting while keeping you in complete control. Unlike spray-and-pray automation bots that spam employers and compromise your reputation, Catchaj enforces strict truth grounding, ruthless fit filtering, and a mandatory human submission handoff so every application you send is authentic, accurate, and intentional.*

### 3.2 Tone of Voice
- **Empathetic & Warm:** Acknowledges the emotional exhaustion of job hunting without sounding cynical or transactional.
- **Editorial & Restrained:** Speaks like a thoughtful publication (e.g., *Stripe Press*, *ReadCV*, *Kinfolk*, *Linear*), not an aggressive B2B enterprise SaaS or growth-hacked Web3 project.
- **Transparent & Unflinching:** Proudly highlights its constraints (e.g., *"Why we refuse to automate the submit button"*, *"Why out-of-area jobs are rejected even with a perfect score"*).
- **Anti-Buzzword Commitment:** Never uses inflated tech jargon. Plain, sharp, conversational English.

### 3.3 Visual & Design DNA
- **Theme Concept:** *"Warm Analog Craft meets Tactile Modern Tech"* (Paper, Ink, Precision, Editorial Elegance).
- **Color Palette:**
  - **Paper Base (`#F5F3EC` / `#FAF9F4`):** Warm, inviting, tactile background reminiscent of archival stationery and high-grade book stock.
  - **Deep Forest Ink (`#27372E`):** Rich, organic dark tone for headlines, primary UI buttons, and strong visual anchors.
  - **Sage & Olive Greens (`#718644` / `#656D63` / `#9BAA72`):** Calm, grounded accents representing health, verification, and thoughtful decision-making.
  - **Lime Accent (`#DCED9D`):** Energetic micro-highlights, badge fills, and status signals.
  - **Cream Line (`#D9DDD0`):** Subtle architectural dividing lines that give structured rhythm without visual noise.
- **Typography:**
  - **Display / Headers:** Crisp, geometric modern sans with tight tracking (`Manrope` or `DM Sans`).
  - **Editorial Accent:** Timeless warm serif (`Georgia`, `Newsreader`, or `Playfair`) used in italics for human emphasis (*"copy-paste"*, *"you decide to press it"*).
  - **Functional UI & Metadata:** Monospace or high-legibility sans (`JetBrains Mono` / `DM Sans` / `Inter`) for scorecards, data pills, and timestamps.

---

## 4. Product Breakdown: The "Six Helpers" System

The website must showcase the core mental model: **A small, specialized digital crew where each helper has a single clear job and strict rules.**

```
┌────────────────────────────────────────────────────────────────────────┐
│                        THE SIX HELPERS PIPELINE                        │
├──────────────┬──────────────┬──────────────┬─────────────┬─────────────┤
│ 01. The      │ 02. The      │ 03. The      │ 04. The     │ 05. The     │
│ Fact-Checker │ Job Scout    │ Strict Judge │ Essay       │ Browser     │
│              │              │              │ Drafter     │ Copilot     │
│ (Career      │ (Discovery   │ (Scoring &   │ (Grounded   │ (Staging    │
│ Truth Doc)   │ & Dedupe)    │ Gatekeeping) │ Tailoring)  │ in Chrome)  │
└──────┬───────┴──────┬───────┴──────┬───────┴──────┬──────┴──────┬──────┘
       │              │              │              │             │
       └──────────────┴──────────────┼──────────────┴─────────────┘
                                     │
                             06. The Privacy Guard
                             (PII / Secret Shields)
                                     │
                             ▼ [THE PAUSE] ▼
                       Human Reviews & Clicks Submit
```

| Helper Name | Operational Role | Working Rule / Product Constraint | Output Artifact |
| :--- | :--- | :--- | :--- |
| **01. The Fact-Checker** | Ingests verified resume & interview notes into an immutable markdown "Truth Document". | *"If it isn't in the Truth Document, it doesn't belong in the answer."* Enforces zero buzzwords. | Verified Candidate Truth Profile |
| **02. The Job Scout** | Scrapes job boards (LinkedIn, Indeed, etc.), fingerprints postings via SHA-256 to eliminate duplicates, and detects the ATS platform. | *"Find the possibilities. Skip the repeats."* Identifies whether an application is frictionless or account-gated. | Deduplicated Opportunity Stream |
| **03. The Strict Judge** | Evaluates fit score (0–100) using LLM reasoning. Applies hard location and platform friction rules. | *"85+ for clean direct forms; 95+ when extra accounts get in the way. Location failure overrides any score."* | Shortlist + Google Sheet Log + Alerts |
| **04. The Essay Drafter** | Inspects postings for unique interview prompts; drafts concise (120–180 word) answers grounded 100% in real candidate facts. | *"Specific beats impressive-sounding. No invented accomplishments; no generic corporate fluff."* | Ready-to-Review Tailored Answers |
| **05. The Browser Copilot** | Launches a visible Chromium window (Playwright), autofills fields, attaches PDF resume, inserts tailored copy, and stages the tab. | *"The last click belongs to you."* Deliberately halts before submission for human review, edits, and CAPTCHA. | Pre-filled Live Browser + Human Handover |
| **06. The Privacy Guard** | Pre-commit Git hooks and local deterministic scanners prevent candidate PII, secrets, or API keys from ever leaking publicly. | *"Keep personal things personal."* Provides synthetic fixtures (e.g., Alex Morgan) for safe demonstrations. | Zero-Leak Sandbox & Protected Credentials |

---

## 5. Website Information Architecture & Page Structure

The website is envisioned as a cohesive, compelling **Product Story & Interactive Case Study**. Below is the recommended layout and module sequencing:

### Section 1: Navigation & Header
- **Brand Mark:** `catchaj.` with the distinctive `j↗` monogram.
- **Status Indicator:** Live pulse dot: `PROTOTYPE WITH INTENT`.
- **Navigation Links:**
  - *The System* (anchors to Six Helpers)
  - *Try the Logic* (anchors to Interactive Playground)
  - *The Pause* (anchors to HITL philosophy)
  - *Behind the Build* (anchors to Architecture/Decisions)
- **Primary CTA:** Text/pill button: *"Explore the Prototype ↗"*.

### Section 2: Hero Section (The Hook & Micro-Showcase)
- **Eyebrow:** `A PRODUCT EXPERIMENT IN HUMAN + AI`
- **Headline:**
  > Your next chapter.  
  > Less of the  
  > *copy-paste.*
- **Sub-headline:**  
  *Job hunting is a full-time job. We built a focused crew of six AI helpers to take the busywork off your plate. They find, filter, draft, and stage. **You make the call.***
- **Hero Interactive Illustration:**  
  A visual split or floating card showing the journey:
  1. *Origin:* A verified "Truth Slip" stamped with candidate facts.
  2. *Connection:* An organic directional arrow.
  3. *Destination:* A structured "Sample Application Card" showing Beacon Health (Lead Product Manager, 92/100 score, verified checks).
  4. *The Focal Stamp:* **"Your turn, human. Review it. Make it yours. Then submit."**

### Section 3: The Three Guiding Principles (Ticker / Ribbon)
A clean, horizontal tactile ribbon bridging the hero and narrative:
- `01` **Facts over fiction** (Strict grounding, zero hallucinations)
- `02` **Fit over volume** (High thresholds, deliberate filters)
- `03` **Assistance over autopilot** (Human judgment at the finish line)

### Section 4: The Manifesto / Problem Section
- **Header:** `THE PROBLEM WORTH SOLVING`
- **Lead Copy:**
  > *Great candidates. Endless busywork.*  
  > The hard part should be finding the right next move—not typing your work history for the forty-seventh time into an antiquated ATS portal.
- **Narrative:**  
  Explain the origin story: starting with a high-stakes wedge (a Senior HealthTech Product Manager), the solution wasn't to generate 500 spammy cover letters, but to eliminate friction for the 5 roles that truly matter.

### Section 5: The Interactive Crew Showcase (The 6 Helpers)
- **UX Pattern:** Dual-column interactive tabbed interface:
  - **Left Column:** Vertical tabs (01 Fact-Checker, 02 Job Scout, 03 Strict Judge, 04 Essay Drafter, 05 Browser Copilot, 06 Privacy Guard) with keyboard accessibility (arrow navigation).
  - **Right Column (Dynamic Stage):** Displays the active helper's icon, operational rule, sample quote, and exact output handoff.
- **Interactive Requirement:** Seamless switching with animated transitions, tactile hover states, and clear focus indicators.

### Section 6: The "Judge's Seat" Interactive Playground
*A signature micro-app on the site that lets visitors play with the actual matching logic:*
- **User Controls:**
  - **Score Slider (0–100):** Adjust role alignment score.
  - **Location Checkbox:** "Within target location (Remote or Seattle local)".
  - **Friction Toggle:** "Requires extra ATS account (Workday / Taleo)".
- **Dynamic Feedback Panel:**
  - *If Location = False:* Immediate rejection badge: **"RIGHT ROLE. WRONG PLACE."** (*"Location is outside target. Role filtered out even at 100/100."*)
  - *If Friction = True & Score < 95:* Rejection badge: **"MORE FRICTION. HIGHER BAR."** (*"Account-gated roles require 95+ to justify candidate time."*)
  - *If Passes:* Green badge: **"WORTH A CLOSER LOOK"** (*"Clears threshold. Logged to pipeline and alert triggered."*)
- **Educational Takeaway:** Proves to the visitor that smart AI is about *restraint*, not indiscriminate spam.

### Section 7: The Centerpiece — "The Most Important Feature is a Pause"
- **Visual Style:** Inverted dark ink section (`#27372E` background, `#F6F4EA` typography).
- **Core Message:**
  > It gets you to the button.  
  > *You decide to press it.*
- **Graphic Element:** An embossed physical "PAUSE STAMP" or tactile button graphic showing `⏸ HUMAN IN THE LOOP`.
- **Copy:** Explain why automated submission is an anti-pattern. Real browser staging prefills the text, attaches the resume, and waits. The candidate edits, reviews, verifies tone, solves any CAPTCHAs, and retains dignity.

### Section 8: Behind the Build / Engineering & Product Craft
- **Section Heading:** `THE CHOICES ARE THE PRODUCT`
- **Three Product Decision Cards:**
  1. *Focus: Optimize for fit, not application count.*
  2. *Trust: Ground the draft, keep the review.*
  3. *Control: Automate the prep, keep the decision.*
- **Tech Stack Badges:** Python • Google Gemini • Playwright • JobSpy • Google Sheets • Human Judgment.
- **Privacy & Security Callout:** Explains the deterministic pre-commit scans, local execution, and the synthetic "Alex Morgan" sandbox fixture.

### Section 9: Closing Call to Action & Footer
- **Closing Headline:**
  > A little help for  
  > your *next big thing.* ↗
- **Secondary CTA:** *"Take the rules for a spin"* / *"View the GitHub Case Study"*.
- **Footer:** Brand mark `catchaj.`, editorial statement (*"A product management × AI building experiment"*), and accessibility / back-to-top links.

---

## 6. Detailed Copywriting & Messaging Bank

### 6.1 Hero & Headline Variations
- *Option A (Editorial & Human):*  
  **Your next chapter. Less of the copy-paste.**  
  *Job hunting is a full-time job. We built a little team to take the busywork off your plate. They find, filter, and draft. You make the call.*
- *Option B (Direct & Punchy):*  
  **High-touch job applications. Zero busywork.**  
  *Six focused AI helpers that scout, evaluate, draft, and stage applications. Grounded in your truth. Paused for your review.*
- *Option C (Philosophical):*  
  **The job application engine that knows when to stop.**  
  *Automate the search, the scoring, and the form-filling. Keep the final say.*

### 6.2 Key Taglines & Soundbites
- *"The hard part should be finding your next move—not re-typing your resume into Workday."*
- *"If it isn't in your Truth Document, it doesn't go in the application."*
- *"We don't build auto-apply bots. We build candidate copilots."*
- *"85 points for a clean application. 95 points when an account gets in the way."*
- *"It gets you right to the button. You decide whether to press it."*

### 6.3 Anti-Buzzword Pledge (Copy Guidelines for the Designer)
Under no circumstances should the website copy include:
- ❌ *"Spearheaded", "Synergy", "Cutting-edge", "Paradigm shift", "Testament to", "Leveraged"*
- ❌ *"Game-changing AI revolution", "10x your applications overnight", "Never write a resume again"*
- ✅ Use concrete verbs: *build, draft, filter, reject, stage, pause, verify, check, review, hand off.*

---

## 7. Interactive Components & Functional Requirements for the Designer

When designing the layout, responsive behavior, and micro-interactions, the designer should prioritize:

1. **Accessibility First (WCAG 2.1 AA Compliant):**
   - Color contrast ratios must exceed 4.5:1 for normal text and 3:1 for large display text.
   - The Six Helpers tab component must fully support keyboard arrow keys (`ArrowUp`, `ArrowDown`, `Home`, `End`), `aria-selected`, and `role="tabpanel"`.
   - Form controls (sliders, toggles) must have associated `<label>` and `<output>` elements.

2. **Responsive Breakpoints & Layouts:**
   - **Desktop (>1180px):** Expansive 2-column hero with floating card illustration; side-by-side interactive playground.
   - **Tablet (768px–1024px):** Condensed grid with natural vertical stacking.
   - **Mobile (320px–480px):** Touch-friendly 44px+ tap targets, horizontally contained hero card (zero horizontal scroll blowout), segmented 2x3 button grid for helper tabs.

3. **Micro-Interactions & Tactile Feedback:**
   - Buttons should feature subtle vertical lift on hover (`transform: translateY(-2px)`).
   - The "Pause Stamp" should feature a gentle organic tilt (5° to 9° rotation) to look hand-stamped.
   - Status indicators (e.g., green pulse dots) should have smooth, continuous breathing animations.

4. **Performance & Lightweight Footprint:**
   - Fast static load: No heavy 3MB JavaScript framework bundles required.
   - Clean HTML5 + CSS3 + vanilla JS.
   - System font fallbacks if web fonts are slow or offline.

---

## 8. Summary Deliverables Checklist for the Web Expert

| Deliverable | Description | Key Focus Area |
| :--- | :--- | :--- |
| **D1. Desktop & Mobile Mockups (Figma / Penpot)** | High-fidelity UI mockups for Desktop (1440px) and Mobile (390px). | Tone, typography hierarchy, warmth of paper/ink theme. |
| **D2. Hero & Card Illustration Art** | Scalable SVG or clean CSS illustration representing the "Truth Doc → Staged Application → Human Pause" journey. | Tactile cards, stamps, and directional flow. |
| **D3. Interactive Playground UI** | Visual states for the 0–100 match slider, location toggle, and friction switch with Pass/Fail feedback cards. | Clear contrast between approved shortlist vs. rejected time-saver. |
| **D4. Component Style Guide** | Colors, typography scale, pill badges, buttons, tab states, and focus indicators. | Editorial precision and accessibility. |
| **D5. Prototype / Static Implementation** | Responsive, accessible HTML/CSS/JS implementation matching or enhancing `docs/index.html`. | Fast loading, accessible ARIA roles, zero layout shift. |

---

*End of Product Marketing Summary & Web Design Handoff Brief for Catchaj.*
