import catalog from "../../data/magasiner.json";
import prices from "../../data/prices_current.json";
import availability from "../../data/availability.json";
import tjenestedata from "../../data/tjenester.json";
import rewritten from "../../data/rewritten.json";

export type Magasin = {
  navn: string;
  slug: string;
  type: "magasin" | "ugeblad";
  forlag: string | null;
  maalgruppe: string | null;
  land: string;
  digitalt: string[];
  ikke_digitalt: boolean;
  lukket: boolean;
  digitalt_bekraeftet?: string[];
  cover?: string;
  print?: { forlag: string; url: string; pris_fra: string | null; udgivelser: number | null; tjekket: string; kilde: string };
  cover_kilde?: string;
  kategori?: string;
  beskrivelse: string;
  kilde: string;
  sidst_tjekket: string | null;
  ai_tekst: boolean;
};

export type Pris = {
  pris: number;
  valuta: string;
  etikett?: string;
  pris_dkk?: number | null;
  kurs?: number;
  kurs_dato?: string;
};

export type TjenestePris = {
  navn: string;
  slug: string;
  hjemmeside: string;
  status: string;
  checked_at: string | null;
  prices: Record<string, Pris>;
};

export const magasiner = catalog as Magasin[];
export const priser = prices as unknown as Record<string, TjenestePris>;
export const tilgaengelighed = availability as unknown as Record<string, Record<string, any>>;
export const omskrevne = rewritten as unknown as Record<string, { tekst?: string; model?: string }>;

/** Foretrækker den omskrevne tekst, falder tilbage til originalen. */
export function bladTekst(m: { slug: string; beskrivelse: string }): string {
  const r = omskrevne[m.slug];
  return (r && r.tekst) ? r.tekst : m.beskrivelse;
}

export const tjenesteInfo = tjenestedata as unknown as Record<string, {
  navn: string; url: string; note: string;
  udenlandske_oplyst: number | null; udenlandske_kilde: string | null;
  danske_kilde: string | null; bemaerkning: string;
  pris_fakta?: { q: string; a: string; kilde: string; hentet: string }[];
}>;

/**
 * Fire tilstande for et blads udvalg hos en tjeneste:
 *  - "bekraeftet": fundet på tjenestens egen side (dato i availability.json)
 *  - "arv": kildesitet markerede bladet hos tjenesten, men vi har ikke verificeret det
 *  - "nej": kilden markerer udtrykkeligt at bladet ikke er digitalt tilgængeligt
 *  - "ukendt": vi ved det ikke
 */
export function udvalgsStatus(slug: string, navn: string, ikkeDigitalt: boolean):
  "bekraeftet" | "arv" | "nej" | "ukendt" {
  const a = tilgaengelighed[slug] || {};
  if (a[navn] === "bekraeftet") return "bekraeftet";
  const m = magasiner.find((x) => x.slug === slug);
  if (m && m.digitalt.some((t) => t.toLowerCase() === navn.toLowerCase())) return "arv";
  // Kilden modsiger sig selv på nogle blade (både "har tjenester" og "ikke digital").
  // Ved modstrid er svaret ukendt — ikke et nej.
  if (ikkeDigitalt && m && m.digitalt.length === 0) return "nej";
  return "ukendt";
}
export const aiDato = "25. oktober 2026";

export const TJENESTER = [
  {
    key: "readly",
    navn: "Readly",
    url: "https://readly.com/da-dk/",
    note: "Størst udvalg, flest internationale titler",
  },
  {
    key: "flipp",
    navn: "Flipp",
    url: "https://flipp.dk/",
    note: "Dansk, stærk på ugeblade og familie",
  },
  {
    key: "pling",
    navn: "Pling",
    url: "https://pling.dk/",
    note: "Dansk, mange nichetitler",
  },
  {
    key: "wype",
    navn: "Wype",
    url: "https://wype.dk/",
    note: "Bladkiosk, kan også købes enkeltvis",
  },
];

/** Formaterer en pris med valuta og omregning. Returnerer "–" når der ikke er data. */
export function prisTekst(p?: Pris): string {
  if (!p) return "–";
  const tal = new Intl.NumberFormat("da-DK", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  if (p.valuta === "DKK") return `${tal.format(p.pris).replace(",00", "")} kr.`;
  const euro = `${tal.format(p.pris)} €`;
  return p.pris_dkk ? `${euro} ≈ ${new Intl.NumberFormat("da-DK", { maximumFractionDigits: 0 }).format(p.pris_dkk)} kr.` : euro;
}

/** Den pris vi viser som "fra" for en tjeneste: billigste af ordinær og tilbud. */
export function billigste(p: Record<string, Pris>): Pris | undefined {
  const list = Object.values(p || {});
  if (!list.length) return undefined;
  return list.reduce((a, b) => ((a.pris_dkk ?? a.pris) <= (b.pris_dkk ?? b.pris) ? a : b));
}

/** Ordinær pris — den pris der gælder efter en eventuel kampagne. */
export function prisHoved(p?: TjenestePris): Pris | undefined {
  if (!p || !p.prices) return undefined;
  return p.prices.ordinary ?? Object.values(p.prices)[0];
}

/** Introduktions- eller kampagnepris, hvis tjenesten har en. */
export function prisIntro(p?: TjenestePris): Pris | undefined {
  if (!p || !p.prices) return undefined;
  return p.prices.intro ?? p.prices.offer ?? p.prices.campaign ?? p.prices.reduced;
}

/** Blade i kataloget hvor tjenesten er bekræftet, opdelt på land. */
export function udvalgFor(navn: string) {
  const danske = magasiner.filter((m) => m.land === "DK" && m.digitalt_bekraeftet?.includes(navn));
  const udenlandske = magasiner.filter((m) => m.land !== "DK" && m.digitalt_bekraeftet?.includes(navn));
  return { danske, udenlandske };
}

/** Deler en tekst i afsnit à ca. 3 sætninger, så en lang beskrivelse ikke bliver én blok. */
export function afsnit(tekst: string, perAfsnit = 3): string[] {
  if (!tekst) return [];
  // Beskyt forkortelser, så "bl.a." ikke bliver delt til "bl." + "a."
  const forkortelser = ["bl.a.", "bl.a", "f.eks.", "fx.", "dvs.", "m.fl.", "m.m.", "osv.",
    "ca.", "evt.", "ift.", "pga.", "tlf.", "kr.", "md.", "nr.", "jf.", "mm.", "ang."];
  let beskyttet = tekst;
  forkortelser.forEach((f, i) => { beskyttet = beskyttet.split(f).join(`\u0000${i}\u0000`); });
  const saetninger = (beskyttet.match(/[^.!?]+[.!?]+["»]?/g) ?? [beskyttet]).map((x) =>
    x.replace(/\u0000(\d+)\u0000/g, (_m, i) => forkortelser[+i]));
  const rene = saetninger.map((x) => x.trim()).filter(Boolean);
  const ud: string[] = [];
  for (let i = 0; i < rene.length; i += perAfsnit) {
    ud.push(rene.slice(i, i + perAfsnit).join(" "));
  }
  return ud;
}

export function tjenesteFor(navn: string) {
  return TJENESTER.find((t) => t.navn.toLowerCase() === navn.toLowerCase());
}

export function harTjeneste(m: Magasin, navn: string) {
  return m.digitalt.some((t) => t.toLowerCase() === navn.toLowerCase());
}
