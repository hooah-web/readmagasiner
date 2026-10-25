import catalog from "../../data/magasiner.json";
import prices from "../../data/prices_current.json";

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

export function tjenesteFor(navn: string) {
  return TJENESTER.find((t) => t.navn.toLowerCase() === navn.toLowerCase());
}

export function harTjeneste(m: Magasin, navn: string) {
  return m.digitalt.some((t) => t.toLowerCase() === navn.toLowerCase());
}
