import type { APIRoute } from "astro";
import { magasiner } from "../lib/site";

export const GET: APIRoute = () => {
  const data = magasiner.map((m) => ({ n: m.navn, s: m.slug, t: m.type }));
  return new Response(JSON.stringify(data), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
};
