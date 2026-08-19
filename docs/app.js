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

let allListings = [];

async function load() {
  const res = await fetch("data/listings.json", { cache: "no-store" });
  const data = await res.json();
  allListings = data.listings || [];
  document.getElementById("meta").textContent =
    `${data.anzahl} Inserate · zuletzt aktualisiert ${formatDate(data.aktualisiert_am)}`;
  populateBundeslandFilter();
  render();
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
  const haystack = `${listing.plz || ""} ${listing.ort || ""}`.toLowerCase();
  return haystack.includes(query.toLowerCase());
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
  const anbieterFilter = document.getElementById("filterAnbieter").value;
  const ortQuery = document.getElementById("filterOrt").value.trim();
  const hideGone = document.getElementById("hideGone").checked;

  const preisMin = numOrNull("preisMin");
  const preisMax = numOrNull("preisMax");
  const flaecheMin = numOrNull("flaecheMin");
  const flaecheMax = numOrNull("flaecheMax");

  let listings = allListings.filter((l) => matchesSearch(l, query));
  if (einschaetzungFilter) {
    listings = listings.filter((l) => l.preis_einschaetzung?.label === einschaetzungFilter);
  }
  if (bundeslandFilter) {
    listings = listings.filter((l) => l.bundesland === bundeslandFilter);
  }
  if (anbieterFilter) {
    listings = listings.filter((l) => l.anbieter_typ === anbieterFilter);
  }
  if (ortQuery) {
    listings = listings.filter((l) => matchesOrt(l, ortQuery));
  }
  if (preisMin !== null || preisMax !== null) {
    listings = listings.filter((l) => inRange(l.preis_eur, preisMin, preisMax));
  }
  if (flaecheMin !== null || flaecheMax !== null) {
    listings = listings.filter((l) => inRange(l.wohnflaeche_m2, flaecheMin, flaecheMax));
  }
  if (hideGone) {
    listings = listings.filter((l) => l.status !== "nicht_mehr_in_trefferliste");
  }
  listings = sortListings(listings, sortMode);

  const container = document.getElementById("cards");
  container.innerHTML = "";
  document.getElementById("empty").hidden = listings.length > 0;

  for (const l of listings) {
    container.appendChild(renderCard(l));
  }
}

function renderCard(l) {
  const el = document.createElement("article");
  el.className = "card" + (l.status === "nicht_mehr_in_trefferliste" ? " gone" : "");

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
      <span>${l.wohnflaeche_m2 ? l.wohnflaeche_m2 + " m²" : "m² unbekannt"}</span>
      <span>${l.preis_pro_m2 ? formatEur(l.preis_pro_m2) + "/m²" : ""}</span>
      <span>${l.baujahr ? "Baujahr " + l.baujahr : "Baujahr unbekannt"}</span>
    </div>
    <div class="badges">
      <span class="badge anbieter-${l.anbieter_typ || ""}">${ANBIETER_LABELS[l.anbieter_typ] || "Anbieter unbekannt"}</span>
      <span class="badge ${einschaetzung.label || ""}" title="${escapeHtml(abweichung)}">${einschaetzungLabel}</span>
      <span class="badge outline">${RENO_LABELS[l.sanierungsstand] || l.sanierungsstand}</span>
      <span class="badge outline">Lage: manuell prüfen</span>
      ${l.status === "nicht_mehr_in_trefferliste" ? '<span class="badge outline">nicht mehr gelistet</span>' : ""}
    </div>
    <p class="card-desc">${escapeHtml((l.beschreibung || "").slice(0, 220))}${(l.beschreibung || "").length > 220 ? "…" : ""}</p>
    ${kiBlock}
    <div class="card-footer">
      <span>Zuerst gesehen: ${formatDate(l.erstgesehen)}</span>
      <span>${abweichung && einschaetzung.abweichung_pct !== undefined ? abweichung : ""}</span>
    </div>
  `;
  return el;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

const liveInputs = ["search", "preisMin", "preisMax", "flaecheMin", "flaecheMax", "filterOrt"];
const changeInputs = ["sortField", "filterEinschaetzung", "filterBundesland", "filterAnbieter", "hideGone"];
liveInputs.forEach((id) => document.getElementById(id).addEventListener("input", render));
changeInputs.forEach((id) => document.getElementById(id).addEventListener("change", render));

document.getElementById("resetFilters").addEventListener("click", () => {
  liveInputs.forEach((id) => (document.getElementById(id).value = ""));
  document.getElementById("filterEinschaetzung").value = "";
  document.getElementById("filterBundesland").value = "";
  document.getElementById("filterAnbieter").value = "";
  document.getElementById("hideGone").checked = false;
  render();
});

load();
