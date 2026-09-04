const LABELS = {
  guenstig: "Günstig",
  im_rahmen: "Im Rahmen",
  teuer: "Teuer",
  zu_wenig_vergleichsdaten: "Zu wenig Vergleichsdaten",
  keine_daten: "Keine Preisdaten",
};

const RENO_LABELS = {
  neubau: "Neubau",
  frisch_saniert: "Frisch saniert",
  saniert_modernisiert: "Saniert/modernisiert",
  sanierungsbeduerftig: "Sanierungsbedürftig",
  unbekannt: "Zustand unbekannt",
};

const ANBIETER_LABELS = {
  privat: "Privat",
  gewerblich: "Gewerblich",
};

const KI_STATUS_LABELS = {
  zu_wenig_text: "KI-Einschätzung: zu wenig Textinformation im Inserat",
  kein_api_key: "KI-Einschätzung nicht verfügbar (kein API-Key konfiguriert)",
  fehler: "KI-Einschätzung fehlgeschlagen",
};

const EXPOSE_CONTACT = {
  firma: "A. Mayer Holding",
  ansprechpartner: "Hasan Süslü",
  telefon: "0177 7041651",
  // TODO: von Hasan bestaetigen lassen, dann hier eintragen
  email: null,
  adresse: null,
};

const LOGO_BASE64 =
  "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";

let allListings = [];
let plzCoords = {};
let activeOrigin = null; // {plz, lat, lon} wenn Umkreissuche aktiv ist

const PAGE_SIZE = 60;
let currentResults = []; // gefilterte+sortierte Treffer der aktuellen render()-Runde
let renderLimit = PAGE_SIZE; // wie viele davon aktuell im DOM stehen
let cardsById = new Map(); // id -> listing, fuer den Expose-Button (Event-Delegation)

async function load() {
  const [listingsRes, coordsRes] = await Promise.all([
    fetch("data/listings.json", { cache: "no-store" }),
    fetch("data/plz_coords.json", { cache: "no-store" }),
  ]);
  const data = await listingsRes.json();
  allListings = data.listings || [];
  plzCoords = await coordsRes.json();
  document.getElementById("meta").textContent =
    `${data.anzahl} Inserate · zuletzt aktualisiert ${formatDate(data.aktualisiert_am)}`;
  populateBundeslandFilter();
  populateObjektTypFilter();
  render();
}

// Luftlinien-Entfernung zwischen zwei Koordinaten (Haversine-Formel), in km.
function haversineKm(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function populateBundeslandFilter() {
  const select = document.getElementById("filterBundesland");
  const values = [...new Set(allListings.map((l) => l.bundesland).filter(Boolean))].sort();
  for (const v of values) {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    select.appendChild(opt);
  }
}

function populateObjektTypFilter() {
  const select = document.getElementById("filterObjektTyp");
  const seen = new Map();
  for (const l of allListings) {
    if (l.objekt_typ) seen.set(l.objekt_typ, l.objekt_typ_label || l.objekt_typ);
  }
  for (const [value, label] of [...seen.entries()].sort((a, b) => a[1].localeCompare(b[1], "de"))) {
    const opt = document.createElement("option");
    opt.value = value;
    opt.textContent = label;
    select.appendChild(opt);
  }
}

function bestFlaeche(l) {
  return l.wohnflaeche_m2 || l.flaeche_m2_sonstige || l.grundstuecksflaeche_m2 || null;
}

function formatDate(iso) {
  if (!iso) return "-";
  const d = new Date(iso);
  return d.toLocaleString("de-DE", { dateStyle: "medium", timeStyle: "short" });
}

function formatEur(n) {
  if (n === null || n === undefined) return "-";
  return new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(n);
}

function matchesSearch(listing, query) {
  if (!query) return true;
  const haystack = `${listing.title || ""} ${listing.ort || ""} ${listing.plz || ""} ${listing.beschreibung || ""}`.toLowerCase();
  return haystack.includes(query.toLowerCase());
}

function sortListings(listings, mode) {
  const withPpm = (l) => (l.preis_pro_m2 === undefined || l.preis_pro_m2 === null ? Infinity : l.preis_pro_m2);
  const copy = [...listings];
  switch (mode) {
    case "preis_pro_m2_asc":
      return copy.sort((a, b) => withPpm(a) - withPpm(b));
    case "preis_pro_m2_desc":
      return copy.sort((a, b) => (b.preis_pro_m2 ?? -1) - (a.preis_pro_m2 ?? -1));
    case "preis_asc":
      return copy.sort((a, b) => (a.preis_eur ?? Infinity) - (b.preis_eur ?? Infinity));
    case "preis_desc":
      return copy.sort((a, b) => (b.preis_eur ?? -1) - (a.preis_eur ?? -1));
    case "neu":
      return copy.sort((a, b) => new Date(b.erstgesehen) - new Date(a.erstgesehen));
    default:
      return copy;
  }
}

function matchesOrt(listing, query) {
  if (!query) return true;
  const q = query.toLowerCase();
  const haystack = `${listing.plz || ""} ${listing.ort || ""}`.toLowerCase();
  // Wort-Praefix-Suche statt reinem substring-Vergleich: "Berlin" soll nicht
  // zufaellig in "Überlingen" matchen (b-e-r-l-i-n steckt da drin). JS-Regex-
  // Wortgrenzen (\b) helfen hier nicht, da Umlaute nicht als \w gelten -
  // stattdessen in echte Woerter zerlegen und Praefix pruefen.
  const tokens = haystack.split(/[^\p{L}\p{N}]+/u).filter(Boolean);
  return tokens.some((t) => t.startsWith(q));
}

function inRange(value, min, max) {
  if (value === null || value === undefined) return min === null && max === null;
  if (min !== null && value < min) return false;
  if (max !== null && value > max) return false;
  return true;
}

function numOrNull(id) {
  const raw = document.getElementById(id).value;
  return raw === "" ? null : Number(raw);
}

function render() {
  const query = document.getElementById("search").value.trim();
  const sortMode = document.getElementById("sortField").value;
  const einschaetzungFilter = document.getElementById("filterEinschaetzung").value;
  const bundeslandFilter = document.getElementById("filterBundesland").value;
  const objektTypFilter = document.getElementById("filterObjektTyp").value;
  const anbieterFilter = document.getElementById("filterAnbieter").value;
  const ortQuery = document.getElementById("filterOrt").value.trim();
  const hideGone = document.getElementById("hideGone").checked;

  const preisMin = numOrNull("preisMin");
  const preisMax = numOrNull("preisMax");
  const flaecheMin = numOrNull("flaecheMin");
  const flaecheMax = numOrNull("flaecheMax");

  const radiusGroup = document.getElementById("radiusGroup");
  const radiusHint = document.getElementById("radiusHint");
  const isPlzQuery = /^\d{5}$/.test(ortQuery);
  activeOrigin = null;
  radiusGroup.hidden = true;
  radiusHint.hidden = true;

  if (isPlzQuery) {
    const coords = plzCoords[ortQuery];
    if (coords) {
      activeOrigin = { plz: ortQuery, lat: coords[0], lon: coords[1] };
      radiusGroup.hidden = false;
    } else {
      radiusHint.hidden = false;
      radiusHint.textContent = `Keine Koordinaten für PLZ ${ortQuery} gefunden — normale Textsuche wird verwendet.`;
    }
  }

  let listings = allListings.filter((l) => matchesSearch(l, query));
  if (einschaetzungFilter) {
    listings = listings.filter((l) => l.preis_einschaetzung?.label === einschaetzungFilter);
  }
  if (bundeslandFilter) {
    listings = listings.filter((l) => l.bundesland === bundeslandFilter);
  }
  if (objektTypFilter) {
    listings = listings.filter((l) => l.objekt_typ === objektTypFilter);
  }
  if (anbieterFilter) {
    listings = listings.filter((l) => l.anbieter_typ === anbieterFilter);
  }
  if (activeOrigin) {
    const radiusKm = Number(document.getElementById("radiusKm").value);
    listings = listings.filter((l) => {
      const coords = l.plz && plzCoords[l.plz];
      if (!coords) return false;
      return haversineKm(activeOrigin.lat, activeOrigin.lon, coords[0], coords[1]) <= radiusKm;
    });
  } else if (ortQuery) {
    listings = listings.filter((l) => matchesOrt(l, ortQuery));
  }
  if (preisMin !== null || preisMax !== null) {
    listings = listings.filter((l) => inRange(l.preis_eur, preisMin, preisMax));
  }
  if (flaecheMin !== null || flaecheMax !== null) {
    listings = listings.filter((l) => inRange(bestFlaeche(l), flaecheMin, flaecheMax));
  }
  if (hideGone) {
    listings = listings.filter((l) => l.status !== "nicht_mehr_in_trefferliste");
  }
  listings = sortListings(listings, sortMode);

  const resultCount = document.getElementById("resultCount");
  resultCount.textContent =
    listings.length === allListings.length
      ? `${listings.length} Inserate`
      : `${listings.length} von ${allListings.length} Inseraten angezeigt`;

  const activeFilterCount = [
    einschaetzungFilter,
    bundeslandFilter,
    objektTypFilter,
    anbieterFilter,
    hideGone,
    preisMin !== null,
    preisMax !== null,
    flaecheMin !== null,
    flaecheMax !== null,
    ortQuery,
  ].filter(Boolean).length;
  const filterCountEl = document.getElementById("filterCount");
  filterCountEl.textContent = activeFilterCount;
  filterCountEl.hidden = activeFilterCount === 0;

  document.getElementById("empty").hidden = listings.length > 0;

  currentResults = listings;
  renderLimit = PAGE_SIZE;
  renderCards();
}

// Baut nur die aktuell sichtbare Seite an Karten (currentResults.slice(0,
// renderLimit)) statt bei jedem Tastendruck alle (teils mehrere Tausend)
// Treffer neu ins DOM zu bauen - das war die Hauptursache dafuer, dass die
// Seite beim Tippen haengen blieb.
function renderCards() {
  const container = document.getElementById("cards");
  const visible = currentResults.slice(0, renderLimit);

  const fragment = document.createDocumentFragment();
  const idToListing = new Map();
  for (const l of visible) {
    idToListing.set(String(l.id), l);
    fragment.appendChild(renderCard(l));
  }
  container.innerHTML = "";
  container.appendChild(fragment);
  cardsById = idToListing;

  const loadMoreContainer = document.getElementById("loadMore");
  const remaining = currentResults.length - visible.length;
  if (remaining > 0) {
    loadMoreContainer.hidden = false;
    loadMoreContainer.textContent = `Weitere ${Math.min(PAGE_SIZE, remaining)} von ${remaining} laden`;
  } else {
    loadMoreContainer.hidden = true;
  }
}

function renderCard(l) {
  const el = document.createElement("article");
  el.className = "card" + (l.status === "nicht_mehr_in_trefferliste" ? " gone" : "");

  let distanceText = "";
  if (activeOrigin && l.plz && plzCoords[l.plz]) {
    const [lat, lon] = plzCoords[l.plz];
    const km = haversineKm(activeOrigin.lat, activeOrigin.lon, lat, lon);
    distanceText = `${Math.round(km)} km von ${activeOrigin.plz}`;
  }

  const einschaetzung = l.preis_einschaetzung || {};
  const einschaetzungLabel = LABELS[einschaetzung.label] || einschaetzung.label || "-";
  const abweichung =
    einschaetzung.abweichung_pct !== undefined
      ? `${einschaetzung.abweichung_pct > 0 ? "+" : ""}${einschaetzung.abweichung_pct}% vs. ${einschaetzung.vergleichsbasis}`
      : einschaetzung.hinweis || "";

  const ki = l.ki_einschaetzung || {};
  const kiBlock =
    ki.status === "ok"
      ? `<p class="card-ki"><span class="card-ki-label">KI-Einschätzung:</span> ${escapeHtml(ki.text)}</p>`
      : ki.status
      ? `<p class="card-ki card-ki-muted">${escapeHtml(KI_STATUS_LABELS[ki.status] || ki.status)}</p>`
      : "";

  el.innerHTML = `
    <a class="card-title" href="${l.url}" target="_blank" rel="noopener">${escapeHtml(l.title || "Ohne Titel")}</a>
    <div class="card-loc">${escapeHtml(l.plz || "")} ${escapeHtml(l.ort || "")}${l.bundesland ? " · " + escapeHtml(l.bundesland) : ""}</div>
    <div class="card-numbers">
      <span><b>${formatEur(l.preis_eur)}</b></span>
      <span>${bestFlaeche(l) ? bestFlaeche(l) + " m²" : "m² unbekannt"}</span>
      <span>${l.preis_pro_m2 ? formatEur(l.preis_pro_m2) + "/m²" : ""}</span>
      <span>${l.baujahr ? "Baujahr " + l.baujahr : "Baujahr unbekannt"}</span>
    </div>
    <div class="badges">
      <span class="badge outline objekt-typ">${escapeHtml(l.objekt_typ_label || l.objekt_typ || "Objekttyp unbekannt")}</span>
      <span class="badge anbieter-${l.anbieter_typ || ""}">${ANBIETER_LABELS[l.anbieter_typ] || "Anbieter unbekannt"}</span>
      <span class="badge ${einschaetzung.label || ""}" title="${escapeHtml(abweichung)}">${einschaetzungLabel}</span>
      <span class="badge outline">${RENO_LABELS[l.sanierungsstand] || l.sanierungsstand}</span>
      <span class="badge outline">Lage: manuell prüfen</span>
      ${l.status === "nicht_mehr_in_trefferliste" ? '<span class="badge outline">nicht mehr gelistet</span>' : ""}
    </div>
    <p class="card-desc">${escapeHtml((l.beschreibung || "").slice(0, 220))}${(l.beschreibung || "").length > 220 ? "…" : ""}</p>
    ${kiBlock}
    <div class="card-footer">
      <span>Zuerst gesehen: ${formatDate(l.erstgesehen)}${distanceText ? " · " + escapeHtml(distanceText) : ""}</span>
      <span>${abweichung && einschaetzung.abweichung_pct !== undefined ? abweichung : ""}</span>
    </div>
    <button type="button" class="expose-btn" data-expose-id="${escapeHtml(String(l.id))}">📄 Exposé erstellen</button>
  `;
  return el;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// Schneidet einen Text auf das letzte vollstaendige Satzende zurueck - die
// KI-Einschaetzung kann durch das max_tokens-Limit mitten im Satz enden,
// was in einem an Externe verschickten Dokument unprofessionell wirkt.
function trimToLastSentence(text) {
  const trimmed = (text || "").trim();
  const match = trimmed.match(/^[\s\S]*[.!?](?=\s|$)/);
  return match ? match[0] : trimmed;
}

// Baut ein eigenstaendiges, druckfertiges Expose fuer ein Objekt.
// Bewusst OHNE Link/Verweis auf das Original-Inserat und ohne den rohen
// Kleinanzeigen-Text (der oft Kontaktdaten des Verkaeufers enthaelt) - das
// Expose soll Interessenten zwingen, ueber A. Mayer Holding Kontakt
// aufzunehmen statt direkt am Verkaeufer vorbei.
function buildExposeHtml(l) {
  const flaeche = bestFlaeche(l);
  const einschaetzung = l.preis_einschaetzung || {};
  const ki = l.ki_einschaetzung || {};
  const ort = [l.plz, l.ort].filter(Boolean).join(" ");
  const ortMitLand = [ort, l.bundesland].filter(Boolean).join(", ");
  const objektart = l.objekt_typ_label || l.objekt_typ || "Immobilie";
  const heute = new Date();
  const standMonatJahr = heute.toLocaleDateString("de-DE", { month: "long", year: "numeric" });

  const kpis = [];
  if (l.preis_eur) kpis.push([formatEur(l.preis_eur), "Kaufpreis"]);
  if (flaeche) kpis.push([`${flaeche} m²`, "Fläche"]);
  if (l.preis_pro_m2) kpis.push([formatEur(l.preis_pro_m2), "Preis pro m²"]);
  if (l.baujahr) kpis.push([String(l.baujahr), "Baujahr"]);
  kpis.push([objektart, "Objektart"]);

  const eckdaten = [
    ["Objektart", objektart],
    ["Standort", ortMitLand || "-"],
  ];
  if (flaeche) eckdaten.push(["Fläche", `ca. ${flaeche} m²`]);
  if (l.zimmer) eckdaten.push(["Zimmer", l.zimmer]);
  if (l.baujahr) eckdaten.push(["Baujahr", l.baujahr]);
  eckdaten.push(["Zustand", RENO_LABELS[l.sanierungsstand] || "unbekannt"]);
  eckdaten.push(["Anbieter", ANBIETER_LABELS[l.anbieter_typ] || "unbekannt"]);

  const bewertung = [];
  if (l.preis_eur) bewertung.push(["Kaufpreis", formatEur(l.preis_eur)]);
  if (l.preis_pro_m2) bewertung.push(["Preis pro m²", formatEur(l.preis_pro_m2)]);
  if (einschaetzung.label) {
    bewertung.push([
      "Markteinschätzung",
      `${LABELS[einschaetzung.label] || einschaetzung.label}${
        einschaetzung.abweichung_pct !== undefined
          ? ` (${einschaetzung.abweichung_pct > 0 ? "+" : ""}${einschaetzung.abweichung_pct}% vs. ${einschaetzung.vergleichsbasis})`
          : ""
      }`,
    ]);
  }
  bewertung.push(["Erstmals erfasst", formatDate(l.erstgesehen)]);

  const highlights = [];
  // Ein "guenstig"-Label mit z.B. -100% Abweichung stammt meist von einem
  // kaputten Platzhalterpreis (z.B. 1 EUR bei Agentur-Inseraten), nicht von
  // einem echten Schnaeppchen - solche Faelle nicht als Highlight bewerben.
  const preisPlausibel = l.preis_eur && l.preis_eur >= 1000;
  const abweichungPlausibel =
    einschaetzung.abweichung_pct === undefined || einschaetzung.abweichung_pct > -80;
  if (einschaetzung.label === "guenstig" && preisPlausibel && abweichungPlausibel) {
    highlights.push(
      `Kaufpreis unter Vergleichsniveau${einschaetzung.abweichung_pct !== undefined ? ` (${einschaetzung.abweichung_pct}% ggü. Marktvergleich)` : ""}`
    );
  }
  if (["neubau", "frisch_saniert"].includes(l.sanierungsstand)) {
    highlights.push("Neuwertiger bzw. frisch sanierter Zustand");
  }
  if (l.anbieter_typ === "privat") {
    highlights.push("Privatverkauf – keine Maklerprovision");
  }
  if (ortMitLand) {
    highlights.push(`Lage: ${ortMitLand}`);
  }
  if (flaeche && l.preis_pro_m2) {
    highlights.push(`${formatEur(l.preis_pro_m2)}/m² bei ca. ${flaeche} m² Fläche`);
  }

  const beschreibung =
    ki.status === "ok"
      ? trimToLastSentence(ki.text)
      : `${objektart} in ${ortMitLand || "unbekannter Lage"}.${flaeche ? ` Fläche ca. ${flaeche} m².` : ""}${
          l.baujahr ? ` Baujahr ${l.baujahr}.` : ""
        } Kaufpreis ${l.preis_eur ? formatEur(l.preis_eur) : "auf Anfrage"}${
          l.preis_pro_m2 ? ` (${formatEur(l.preis_pro_m2)}/m²)` : ""
        }.`;

  const kontaktZeilen = [
    [EXPOSE_CONTACT.firma, EXPOSE_CONTACT.ansprechpartner].filter(Boolean).join(" · "),
    EXPOSE_CONTACT.telefon ? `Tel. ${EXPOSE_CONTACT.telefon}` : "",
    EXPOSE_CONTACT.email || "",
    EXPOSE_CONTACT.adresse || "",
  ].filter(Boolean);

  const esc = escapeHtml;

  return `<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>${esc(objektart)} – ${esc(ort)} | Investmentexposé</title>
<style>
  @page { size: A4; margin: 0; }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0;
    font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
    color: #12233f;
    background: #fdfcfa;
    -webkit-font-smoothing: antialiased;
  }
  .page {
    width: 210mm;
    min-height: 297mm;
    padding: 14mm 16mm 12mm;
    position: relative;
  }
  .head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
  }
  .eyebrow {
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #ef8f3f;
    text-transform: uppercase;
    margin: 0 0 8px;
  }
  h1 {
    margin: 0 0 8px;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 26px;
    font-weight: 700;
    line-height: 1.25;
    color: #12233f;
    max-width: 145mm;
  }
  .intro {
    margin: 0;
    font-size: 12px;
    line-height: 1.6;
    color: #33415c;
    max-width: 150mm;
  }
  .logo {
    flex: none;
    width: 30mm;
    height: auto;
  }
  .infoline {
    margin: 10px 0 0;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.06em;
    color: #ef8f3f;
    text-transform: uppercase;
  }
  .infoline span:not(:last-child)::after {
    content: "•";
    margin: 0 8px;
    color: #e3c8ab;
  }

  .kpis {
    display: flex;
    gap: 8px;
    margin-top: 16px;
  }
  .kpi {
    flex: 1;
    background: #ffffff;
    border: 1px solid #ef8f3f;
    border-radius: 8px;
    padding: 10px 8px;
    text-align: center;
  }
  .kpi .v {
    font-size: 16px;
    font-weight: 800;
    color: #12233f;
    line-height: 1.15;
  }
  .kpi .l {
    margin-top: 3px;
    font-size: 8.5px;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #ef8f3f;
  }

  .boxes {
    display: flex;
    gap: 10px;
    margin-top: 14px;
  }
  .box {
    flex: 1;
    background: #ffffff;
    border: 1px solid #e7dfd2;
    border-radius: 10px;
    padding: 12px 14px;
  }
  .box h2 {
    margin: 0 0 8px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #ef8f3f;
  }
  .box p {
    margin: 0 0 8px;
    font-size: 11px;
    line-height: 1.55;
    color: #33415c;
  }
  table.facts {
    width: 100%;
    border-collapse: collapse;
  }
  table.facts td {
    font-size: 10.5px;
    padding: 3.5px 0;
    border-top: 1px solid #f0ece2;
    vertical-align: top;
  }
  table.facts td:first-child {
    color: #7c8598;
    width: 42%;
  }
  table.facts td:last-child {
    color: #12233f;
    font-weight: 600;
    text-align: right;
  }

  .pricebar {
    margin-top: 10px;
    background: #12233f;
    border-radius: 10px;
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .pricebar .label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: #b9c3d6;
  }
  .pricebar .value {
    font-size: 20px;
    font-weight: 800;
    color: #ef8f3f;
  }

  .highlights {
    margin-top: 14px;
  }
  .highlights h2 {
    margin: 0 0 8px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #ef8f3f;
  }
  .highlights ul {
    margin: 0;
    padding: 0;
    list-style: none;
    columns: 2;
    column-gap: 24px;
  }
  .highlights li {
    font-size: 10.5px;
    line-height: 1.5;
    color: #33415c;
    padding-left: 16px;
    position: relative;
    margin-bottom: 5px;
    break-inside: avoid;
  }
  .highlights li::before {
    content: "✓";
    position: absolute;
    left: 0;
    color: #ef8f3f;
    font-weight: 800;
  }

  .disclaimer {
    margin-top: 14px;
    background: #f7f4ee;
    border-radius: 8px;
    padding: 9px 12px;
  }
  .disclaimer .t {
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: #ef8f3f;
    margin-bottom: 3px;
  }
  .disclaimer p {
    margin: 0;
    font-size: 8.5px;
    line-height: 1.5;
    color: #7c8598;
  }

  footer {
    position: absolute;
    bottom: 10mm;
    left: 16mm;
    right: 16mm;
    border-top: 1px solid #e7dfd2;
    padding-top: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 9.5px;
    color: #7c8598;
  }
  footer .contact {
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
  }
  footer b {
    color: #12233f;
  }

  .print-bar {
    max-width: 210mm;
    margin: 10px auto;
    padding: 0 16mm;
    display: flex;
    justify-content: flex-end;
  }
  .print-bar button {
    padding: 8px 16px;
    border-radius: 8px;
    border: none;
    background: #ef8f3f;
    color: white;
    font-weight: 700;
    font-size: 13px;
    cursor: pointer;
  }
  @media print {
    .print-bar { display: none; }
    body { background: white; }
  }
</style>
</head>
<body>
<div class="print-bar"><button onclick="window.print()">Als PDF speichern / Drucken</button></div>
<div class="page">
  <div class="head">
    <div>
      <p class="eyebrow">${esc((l.bundesland || l.ort || "Deutschland").toUpperCase())} · ${esc(objektart.toUpperCase())} · VERTRAULICH</p>
      <h1>${esc((l.title || objektart).slice(0, 110))}</h1>
      <p class="intro">${esc(beschreibung)}</p>
    </div>
    <img class="logo" src="data:image/png;base64,${LOGO_BASE64}" alt="Mayer Consulting Logo">
  </div>

  <p class="infoline"><span>Verkaufsangebot</span><span>Stand ${esc(standMonatJahr)}</span><span>Vertraulich</span></p>

  <div class="kpis">
    ${kpis
      .slice(0, 5)
      .map(([v, l2]) => `<div class="kpi"><div class="v">${esc(v)}</div><div class="l">${esc(l2)}</div></div>`)
      .join("")}
  </div>

  <div class="boxes">
    <div class="box">
      <h2>Objekt &amp; Eckdaten</h2>
      <table class="facts">
        ${eckdaten.map(([k, v]) => `<tr><td>${esc(k)}</td><td>${esc(String(v))}</td></tr>`).join("")}
      </table>
    </div>
    <div class="box">
      <h2>Markteinschätzung</h2>
      <table class="facts">
        ${bewertung.map(([k, v]) => `<tr><td>${esc(k)}</td><td>${esc(String(v))}</td></tr>`).join("")}
      </table>
    </div>
  </div>

  ${
    l.preis_eur
      ? `<div class="pricebar"><span class="label">Kaufpreis</span><span class="value">${esc(formatEur(l.preis_eur))}</span></div>`
      : ""
  }

  ${
    highlights.length
      ? `<div class="highlights"><h2>Investment-Highlights</h2><ul>${highlights
          .slice(0, 7)
          .map((h) => `<li>${esc(h)}</li>`)
          .join("")}</ul></div>`
      : ""
  }

  <div class="disclaimer">
    <div class="t">Hinweis</div>
    <p>Alle Angaben in diesem Exposé wurden nach bestem Wissen auf Basis öffentlich zugänglicher Angebotsdaten zusammengestellt. Für die Richtigkeit und Vollständigkeit wird keine Haftung übernommen. Preis- und Markteinschätzungen sind automatisiert erstellte Anhaltspunkte, kein Wertgutachten. Änderungen, Irrtümer und Zwischenverkauf bleiben vorbehalten.</p>
  </div>

  <footer>
    <span class="contact">${kontaktZeilen.map((z, i) => (i === 0 ? `<b>${esc(z)}</b>` : esc(z))).join(" · ")}</span>
    <span>Stand ${esc(standMonatJahr)}</span>
  </footer>
</div>
</body>
</html>`;
}

function openExpose(l) {
  const html = buildExposeHtml(l);
  const blob = new Blob([html], { type: "text/html" });
  const url = URL.createObjectURL(blob);
  window.open(url, "_blank");
}

function debounce(fn, waitMs) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), waitMs);
  };
}

// Bei mehreren Tausend Inseraten kostet ein render() spuerbar Zeit (DOM-Bau
// pro Karte) - ohne Debounce loest jeder einzelne Tastendruck/Slider-Schritt
// einen vollen Re-Render aus, was die Seite beim Tippen haengen laesst.
const debouncedRender = debounce(render, 200);

const liveInputs = ["search", "preisMin", "preisMax", "flaecheMin", "flaecheMax", "filterOrt", "radiusKm"];
const changeInputs = [
  "sortField",
  "filterEinschaetzung",
  "filterBundesland",
  "filterObjektTyp",
  "filterAnbieter",
  "hideGone",
];
liveInputs.forEach((id) => document.getElementById(id).addEventListener("input", debouncedRender));
changeInputs.forEach((id) => document.getElementById(id).addEventListener("change", render));

// Event-Delegation statt eines addEventListener pro Karte - bei Tausenden
// Karten pro Render sonst unnoetig teuer.
document.getElementById("cards").addEventListener("click", (e) => {
  const btn = e.target.closest(".expose-btn");
  if (!btn) return;
  const listing = cardsById.get(btn.dataset.exposeId);
  if (listing) openExpose(listing);
});

document.getElementById("loadMore").addEventListener("click", () => {
  renderLimit += PAGE_SIZE;
  renderCards();
});

document.getElementById("filtersToggle").addEventListener("click", () => {
  const panel = document.getElementById("filtersPanel");
  const collapsed = panel.classList.toggle("collapsed");
  document.getElementById("filtersToggle").setAttribute("aria-expanded", String(!collapsed));
});

document.getElementById("radiusKm").addEventListener("input", (e) => {
  document.getElementById("radiusKmLabel").textContent = `${e.target.value} km`;
});

document.getElementById("resetFilters").addEventListener("click", () => {
  liveInputs.filter((id) => id !== "radiusKm").forEach((id) => (document.getElementById(id).value = ""));
  document.getElementById("radiusKm").value = 50;
  document.getElementById("radiusKmLabel").textContent = "50 km";
  document.getElementById("filterEinschaetzung").value = "";
  document.getElementById("filterBundesland").value = "";
  document.getElementById("filterObjektTyp").value = "";
  document.getElementById("filterAnbieter").value = "";
  document.getElementById("hideGone").checked = false;
  render();
});

load();
