---
name: sumsub-theme-msdk
description: Analyze a native mobile app's design system (colors, fonts, corner radii, margins, light/dark) and generate code that themes the Sumsub Mobile SDK to match it — Swift (SNSTheme subclass) on iOS, Kotlin (SNSTheme DSL) on Android. Use this whenever the user wants the Sumsub verification / KYC screens to match their app's look — "theme / brand / style the Sumsub SDK", "make the verification screen match my app", "match my KYC flow colors and fonts", "customize SNSMobileSDK appearance" — including when they don't say "theme" but ask to align the SDK's colors / fonts with their app. Detects the platform from the project (iOS Xcode/Swift vs Android Gradle/Kotlin). Scans for design tokens (iOS — asset-catalog `.colorset`, `Color`/`UIColor` & `Font` extensions, accent / tint; Android — `colors.xml` / `themes.xml` / `values-night`, Compose `ColorScheme` / `Typography`), derives a full palette, and writes the theme file. SKIP for theming the host app itself (this only styles the Sumsub SDK), web theming, and the SDK integration / setup (use `sumsub-integrate-msdk`).
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Sumsub — Mobile SDK theming (iOS & Android)

Scan the host app's design system, derive a full palette, and write a theme the SDK picks
up at launch — **iOS:** a `SumsubTheme: SNSTheme` subclass assigned as
`sdk.theme = SumsubTheme()`; **Android:** a `sumsubTheme(context)` factory built with the
`SNSTheme { … }` DSL and attached via `SNSMobileSDK.Builder(...).withTheme(...)` — so the
KYC screens match the app instead of looking bolted on. Every SDK theme property is either
mapped from the app or explicitly derived; nothing is left at the SDK default by accident.

This is the **trunk** (always-on). Detect the platform, then walk that track's four
stages in order: Scan → Map → Generate → Report.

## Asking vs doing — keep approvals meaningful

- **Read-only is free** — scan / grep / read the project's colors, fonts and build settings without asking.
- **Batch mutations into one approval**, not one per item ("I'll write `SumsubTheme.swift` here + insert this `sdk.theme = …` line [diff] — apply?").
- **Ask explicitly only for:** the target file path, genuinely ambiguous brand / legibility / font choices, and editing existing app code (the single theme-attachment line — the skill adds it itself, never punts it to the user).

## Detect the platform (do this before opening any stage file)

Decide whether this is an **iOS** or **Android** project — the token sources, the theme
API, and the generated language all differ. Read-only.

```bash
# iOS markers
find . -maxdepth 3 \( -name '*.xcodeproj' -o -name '*.xcworkspace' -o -name 'Podfile' -o -name 'Package.swift' \) 2>/dev/null
# Android markers
find . -maxdepth 3 \( -name 'build.gradle' -o -name 'build.gradle.kts' -o -name 'settings.gradle*' -o -name 'AndroidManifest.xml' \) 2>/dev/null
```

- **iOS only** → iOS track. **Android only** → Android track.
- **Both present** → report both and **ask which platform to theme.** One platform per run.
  (React Native / Flutter wrappers are out of scope — this skill themes the native SDKs.)
- **Neither** → ask the user to point at the app's source root.

## How to navigate this skill

A strictly linear flow per track — walk the four stages in order; each is self-contained
and ends with a **Next** pointer.

### iOS track

1. [`ios/stages/1-scan.md`](ios/stages/1-scan.md) — scan the host app's design system (read-only).
2. [`ios/stages/2-map.md`](ios/stages/2-map.md) — map tokens onto the SDK theme (after resolving open decisions).
3. [`ios/stages/3-generate.md`](ios/stages/3-generate.md) — write `SumsubTheme.swift` (after the path is confirmed).
4. [`ios/stages/4-report.md`](ios/stages/4-report.md) — present the coverage report.

### Android track

1. [`android/stages/1-scan.md`](android/stages/1-scan.md) — scan the host app's design system (read-only).
2. [`android/stages/2-map.md`](android/stages/2-map.md) — map tokens onto the SDK theme (after resolving open decisions).
3. [`android/stages/3-generate.md`](android/stages/3-generate.md) — write `SumsubTheme.kt` (after the path is confirmed).
4. [`android/stages/4-report.md`](android/stages/4-report.md) — present the coverage report.

> **Fallback (last resort only).** This skill and its stage files are the primary source —
> don't reach for external docs by default. Only if you hit a genuine blocker they don't
> resolve, consult the Sumsub theme docs:
> [iOS](https://docs.sumsub.com/docs/sdk-theme-api) ·
> [Android](https://docs.sumsub.com/docs/android-theme-api).

When the stages are walked, return here for **Guardrails** and **Handoff**.

## Guardrails — what this skill must never do

- **Never write the file without confirming the path** with the user.
- **Never leave a property at SDK default without noting it** in the report.
- **Never hard-code arbitrary values** — colors come from the app palette or the documented alpha-derivation.
- **Always show the hex** (or asset / resource name) when reporting or asking; add a plain-word description in parentheses, never instead of the hex.
- **Never silently guess a genuinely ambiguous choice** — offer plain-word options + a recommendation; but don't over-ask where a safe default exists.
- **Never theme the host app itself** — only the Sumsub SDK screens.
- **Never change SDK integration logic** (install / init / present / launch). The skill's one edit to existing code is attaching the theme at the launch site — it makes that edit itself, with approval.
- **(iOS) Never emit unsafe color/font code** — no flat `UIColor` literals for dual-appearance apps (use named assets or `UIColor { traits in … }`); no `UIFont(name:size:)` without a `?? .systemFont(…)` fallback; no decorative/app colors in the success/warning/critical slots.
- **(iOS) Never override `images.*` for verification-flow icons** — Sumsub-specific, not derivable from the host.
- **(Android) Never emit single-appearance colors for a dual-appearance app** — resolve both variants and use the two-argument `SNSThemeColor(light, dark)`; no `ResourcesCompat.getFont` result without a `?: Typeface.…` fallback.
- **(Android) Never override the SDK's `sns_*` resources** (colors / strings / drawables in the host's `res/`) — theme through the Theme API only; resource overrides fight the theme and break on SDK updates.
- **(Android) Attach the theme on the builder** — `.withTheme(...)` before `.build()`; never try to restyle after `launch()`.

## Handoff

After the file is generated and wired, summarise:

1. **File created** — `SumsubTheme.swift` / `SumsubTheme.kt` and where it lives (iOS: confirm it's a target member; Android: any location under a source set compiles).
2. **Coverage** — the Stage 4 report (mapped / derived / left at default), plus any contrast fix or choice the user made.
3. **Wiring done** — the exact launch site (file:line) where the theme is attached (iOS: `sdk.theme = SumsubTheme()` or `SumsubTheme.make()`; Android: `.withTheme(sumsubTheme(activity))` on the builder). If no integration code was found (SDK not wired up yet), say so and point to [`sumsub-integrate-msdk`](../sumsub-integrate-msdk/SKILL.md) — the theme is ready to attach once it is.
