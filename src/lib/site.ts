import catalog from "../../data/magasiner.json";
import prices from "../../data/prices_current.json";
import availability from "../../data/availability.json";
import tjenestedata from "../../data/tjenester.json";

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

/** Beskrivelsen ligger nu i magasiner.json — der er ikke længere en separat omskrevet fil. */
export function bladTekst(m: { slug: string; beskrivelse: string }): string {
  return m.beskrivelse ?? "";
}

export const tjenesteInfo = tjenestedata as unknown as Record<string, {
  navn: string; url: string; note: string;
  udenlandske_oplyst: number | null; udenlandske_kilde: string | null;
  udvalg_i_alt?: number | null;
  beskrivelse?: string | null;
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
  // Tjenestens egen liste er sandheden: står bladet ikke på den, er svaret nej.
  if (a[navn] === "nej") return "nej";
  const m = magasiner.find((x) => x.slug === slug);
  if (m && m.digitalt.some((t) => t.toLowerCase() === navn.toLowerCase())) return "arv";
  // Kilden modsiger sig selv på nogle blade (både "har tjenester" og "ikke digital").
  // Ved modstrid er svaret ukendt — ikke et nej.
  if (ikkeDigitalt && m && m.digitalt.length === 0) return "nej";
  return "ukendt";
}
export const aiDato = "25. oktober 2026";

/** 2026-10-25 -> 25.10.2026. Tomt input giver tom streng. */
export function danskDato(iso?: string | null): string {
  if (!iso) return "";
  const d = String(iso).slice(0, 10);
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(d);
  return m ? `${m[3]}.${m[2]}.${m[1]}` : d;
}

export const TJENESTER = [
  {
    key: "readly",
    navn: "Readly",
    url: "https://readly.com/da-dk/",
    note: "Svensk tjeneste med danske og udenlandske blade",
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

/* ---------------------------------------------------------------------------
   SEO — titler og meta-beskrivelser

   Regler: titel maks 60 tegn (Google klipper omkring 580 px), beskrivelse
   140-158 tegn. Alle skal være unikke, og titlen skal sige hvad siden giver,
   ikke bare gentage bladets navn. Derfor bygges de af data, ikke af skabeloner
   med fast ordlyd.
   --------------------------------------------------------------------------- */

const SET_NAVN = "readmagasiner.dk";

function klip(tekst: string, maks: number): string {
  if (tekst.length <= maks) return tekst;
  const klippet = tekst.slice(0, maks);
  const sidsteMellemrum = klippet.lastIndexOf(" ");
  return (sidsteMellemrum > maks * 0.6 ? klippet.slice(0, sidsteMellemrum) : klippet).replace(/[,;:–-]$/, "");
}

/** Første hele sætning af bladets egen beskrivelse — bruges til at gøre meta unik. */
const HÆNG = new Set(["der","som","og","med","til","for","i","på","af","at","den","det","en","et","om","fra","ved","men","eller","hvor","når","fordi"]);

function renSætning(tekst: string, maks: number): string {
  const ren = (tekst || "").replace(/\s+/g, " ").trim();
  const m = /^(.{30,}?[.!?])(\s|$)/.exec(ren);
  let ud = (m ? m[1] : ren).replace(/[.!?]$/, "");
  if (ud.length > maks) {
    const kandidat = ud.slice(0, maks);
    const komma = kandidat.lastIndexOf(", ");
    // helst et komma, så sætningen ikke ender midt i en ledsætning
    ud = komma > maks * 0.55 ? kandidat.slice(0, komma) : kandidat;
    if (ud === kandidat) {
      const mellemrum = ud.lastIndexOf(" ");
      if (mellemrum > maks * 0.55) ud = ud.slice(0, mellemrum);
    }
    // fjern hængende bindeord, så sætningen ikke ender med "der" eller "og"
    let ord = ud.split(" ");
    while (ord.length > 3 && HÆNG.has(ord[ord.length - 1].toLowerCase().replace(/[,;:]$/, ""))) ord.pop();
    ud = ord.join(" ").replace(/[,;:–-]$/, "");
  }
  return ud;
}

/** Vælger den kombination der kommer tættest på 130-158 tegn. */
function bedsteUtfald(dele: string[], maks = 158, min = 130): string {
  for (let antal = dele.length; antal >= 1; antal--) {
    const tekst = dele.slice(0, antal).join(" ").replace(/\s+/g, " ").trim();
    if (tekst.length <= maks && tekst.length >= min) return tekst;
  }
  const kort = dele.filter(Boolean).join(" ").replace(/\s+/g, " ").trim();
  return klip(kort, maks);
}

export function seoTitel(m: Magasin): string {
  const tjenester = m.digitalt;
  const base =
    tjenester.length >= 2
      ? `${m.navn}: læs hos ${tjenester[0]} og ${tjenester[1]}`
      : tjenester.length === 1
        ? `${m.navn}: læs digitalt hos ${tjenester[0]}`
        : `${m.navn}: digital tilgængelighed og pris`;
  const medMærke = `${base} | ${SET_NAVN}`;
  return medMærke.length <= 60 ? medMærke : klip(base, 58);
}

export function seoBeskrivelse(m: Magasin): string {
  const tjenester = m.digitalt;
  const hos = tjenester.length >= 2 ? `${tjenester[0]} og ${tjenester[1]}` : tjenester[0] ?? "";
  const start = renSætning(m.beskrivelse ?? "", 86);
  return bedsteUtfald([
    start ? start + "." : "",
    tjenester.length ? `Kan læses digitalt hos ${hos}.` : "Ingen af de fire tjenester har bladet.",
    "Se pris og udvalg.",
    "Vi viser hvornår prisen sidst er tjekket.",
    "Sammenlign de fire tjenester, før du vælger.",
  ]);
}

export function seoTjenesteTitel(navn: string): string {
  const base = `${navn}: pris, udvalg og vilkår`;
  const medMærke = `${base} | ${SET_NAVN}`;
  return medMærke.length <= 60 ? medMærke : klip(base, 58);
}

export function seoTjenesteBeskrivelse(navn: string, antalDanske: number, pris: string, ekstra: string, tjekket?: string): string {
  return bedsteUtfald([
    `${navn}: ${antalDanske} danske blade i vores registrering.`,
    `Pris ${pris} om måneden.`,
    ekstra,
    tjekket ? `Prisen er tjekket ${tjekket}.` : "",
  ]);
}
