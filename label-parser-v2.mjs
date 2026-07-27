/**
 * ParaMat label parser v2.
 *
 * Converts OCR text into reviewable candidate facts. It does not certify,
 * authenticate, or automatically publish any extracted field.
 */

const MATERIAL_PATTERN =
  /\b(PLA(?:\+| PLUS)?|PETG|PET-?G|ABS|ASA|TPU|TPE|PVA|PVB|PCTG|PET|HIPS|PC|PA\d*|PA-?CF|PA-?GF|PP|PPS(?:-?GF\d*|-?CF\d*)?|PEEK|PEKK|PSU|PPSU)\b/i;

const COLOR_WORDS = [
  "black", "white", "gray", "grey", "red", "orange", "yellow", "green", "blue", "purple",
  "violet", "pink", "brown", "beige", "natural", "clear", "transparent", "translucent", "silver",
  "gold", "bronze", "copper", "navy", "cyan", "magenta", "ivory",
];

const EFFECT_WORDS = [
  "matte", "silk", "satin", "gloss", "glossy", "sparkle", "galaxy", "marble", "wood",
  "metallic", "fluorescent", "glow", "gradient", "dual color", "tri color", "carbon fiber",
  "glass fiber",
];

const GENERIC_LINES =
  /^(?:3d\s*printer\s*)?filament|premium|high quality|net weight|diameter|printing temperature|bed temperature|made in|www\.|https?:/i;

export function normalizeOcrText(value) {
  return String(value ?? "")
    .replace(/[℃]/g, "°C")
    .replace(/[‐‑‒—]/g, "–")
    .replace(/\b(?=[\dOo]*\d)[\dOo]{2,4}\b/g, (token) => token.replace(/[oO]/g, "0"))
    .replace(/[ \t]+/g, " ")
    .trim();
}

export function explicitFlameStatement(value) {
  const text = normalizeOcrText(value);
  const ul94 = text.match(/\bUL[\s-]?94(?:[\s:-]*(V[\s-]?[012]|HB|5VA|5VB))?\b/i);
  if (ul94) {
    const rating = ul94[1]?.toUpperCase().replace(/\s+/, "-");
    return {
      value: rating ? `UL94 ${rating}` : "UL94-rated",
      evidence: ul94[0],
      status: "as_stated_unverified",
    };
  }

  const phrase = text.match(/\bflame[- ]?retard(?:ant|ancy)\b|\bflame[- ]?resistant\b/i);
  if (phrase) {
    return {
      value: "Flame-retardant",
      evidence: phrase[0],
      status: "as_stated_unverified",
    };
  }

  // Bare V0/V-0 and FR are deliberately rejected.
  return null;
}

function candidate(value, unit, evidence, confidence = "pattern") {
  return value == null
    ? null
    : { value, ...(unit ? { unit } : {}), evidence, confidence, review: "unreviewed" };
}

function parseRange(text, patterns, minimum, maximum, unit) {
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (!match) continue;
    const low = Number(match[1]);
    const high = Number(match[2] ?? match[1]);
    if (
      Number.isFinite(low) &&
      Number.isFinite(high) &&
      low >= minimum &&
      high <= maximum &&
      low <= high
    ) {
      return candidate([low, high], unit, match[0]);
    }
  }
  return null;
}

function parseBrand(text, knownBrands) {
  const normalized = text.toLowerCase();
  const matches = [...new Set(knownBrands)]
    .filter((brand) => {
      const needle = String(brand).trim().toLowerCase();
      return needle.length >= 3 && normalized.includes(needle);
    })
    .sort((a, b) => String(b).length - String(a).length);
  return matches.length ? candidate(matches[0], null, matches[0], "catalog_anchor") : null;
}

function parseProductName(text, brand, family) {
  const lines = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length >= 3 && line.length <= 80 && !GENERIC_LINES.test(line));
  const scored = lines
    .map((line) => {
      let score = 0;
      if (brand && line.toLowerCase().includes(String(brand.value).toLowerCase())) score += 3;
      if (family && line.toUpperCase().includes(String(family.value).toUpperCase())) score += 2;
      if (/[A-Za-z]{3}/.test(line)) score += 1;
      if (/\d{3}\s*°?\s*C|\d+\s*mm|\d+\s*(?:kg|g)\b/i.test(line)) score -= 4;
      return { line, score };
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score || a.line.length - b.line.length);
  return scored.length ? candidate(scored[0].line, null, scored[0].line, "heuristic") : null;
}

export function parseFilamentLabel(value, options = {}) {
  const rawText = String(value ?? "").trim();
  const text = normalizeOcrText(rawText);
  const materialMatch = text.match(MATERIAL_PATTERN);
  const family = materialMatch
    ? candidate(materialMatch[1].toUpperCase().replace("PET-G", "PETG"), null, materialMatch[0])
    : null;

  const nozzleTemperature = parseRange(
    text,
    [
      /(?:nozzle|print(?:ing)?\s*temp\w*|hotend|extruder)\D{0,18}(\d{2,3})(?:\s*°?\s*C?\s*[-–~to]+\s*(\d{2,3}))?/i,
      /\b(\d{3})\s*°?\s*C?\s*[-–~]\s*(\d{3})\s*°?\s*C\b/i,
    ],
    140,
    500,
    "°C",
  );

  const bedTemperature = parseRange(
    text,
    [
      /(?:heated?\s*bed|heatbed|\bbed\b|platform)\D{0,18}(\d{1,3})(?:\s*°?\s*C?\s*[-–~to]+\s*(\d{1,3}))?/i,
    ],
    0,
    150,
    "°C",
  );

  const speed = parseRange(
    text,
    [
      /(?:print(?:ing)?\s*speed|speed)\D{0,18}(\d{1,4})(?:\s*[-–~to]+\s*(\d{1,4}))?\s*mm\s*\/?\s*s/i,
      /\b(\d{2,4})(?:\s*[-–~]\s*(\d{2,4}))?\s*mm\s*\/?\s*s\b/i,
    ],
    1,
    2000,
    "mm/s",
  );

  const coolingFan = parseRange(
    text,
    [
      /(?:part\s*)?(?:cooling\s*)?fan(?:\s*speed)?\D{0,18}(\d{1,3})(?:\s*(?:[-\u2013~]|to)\s*(\d{1,3}))?\s*%/i,
    ],
    0,
    100,
    "%",
  );

  const flowRatioDecimal = text.match(
    /(?:flow\s*(?:ratio|multiplier)|extrusion\s*multiplier)\D{0,14}(\d(?:[.,]\d{1,3})?)/i,
  );
  const flowPercent = text.match(
    /(?:^|[\s,;])(?:flow|extrusion\s*flow)\D{0,10}(\d{2,3}(?:[.,]\d+)?)\s*%/i,
  );
  let flowRatio = null;
  if (flowRatioDecimal) {
    const value = Number(flowRatioDecimal[1].replace(",", "."));
    if (Number.isFinite(value) && value >= 0.5 && value <= 1.5) {
      flowRatio = candidate(value, "ratio", flowRatioDecimal[0]);
    }
  } else if (flowPercent) {
    const value = Number(flowPercent[1].replace(",", ".")) / 100;
    if (Number.isFinite(value) && value >= 0.5 && value <= 1.5) {
      flowRatio = candidate(value, "ratio", flowPercent[0]);
    }
  }

  const volumetricMatch = text.match(
    /(?:max(?:imum)?\s*)?(?:volumetric|volume)\s*(?:flow|speed|rate)?\D{0,18}(\d{1,3}(?:[.,]\d+)?)\s*mm\s*(?:3|\u00B3)\s*\/?\s*s/i,
  );
  let maxVolumetricSpeed = null;
  if (volumetricMatch) {
    const value = Number(volumetricMatch[1].replace(",", "."));
    if (Number.isFinite(value) && value >= 0.1 && value <= 100) {
      maxVolumetricSpeed = candidate(value, "mm\u00B3/s", volumetricMatch[0]);
    }
  }

  const retractionMatch = text.match(
    /retract(?:ion|ing)?\D{0,18}(\d{1,2}(?:[.,]\d+)?)\s*mm(?:\D{0,18}?(\d{1,3}(?:[.,]\d+)?)\s*mm\s*\/?\s*s)?/i,
  );
  let retraction = null;
  if (retractionMatch) {
    const distance = Number(retractionMatch[1].replace(",", "."));
    const speedValue = retractionMatch[2]
      ? Number(retractionMatch[2].replace(",", "."))
      : null;
    if (
      Number.isFinite(distance) &&
      distance >= 0 &&
      distance <= 20 &&
      (speedValue == null || (Number.isFinite(speedValue) && speedValue >= 1 && speedValue <= 200))
    ) {
      retraction = {
        distance: candidate(distance, "mm", retractionMatch[0]),
        speed: speedValue == null ? null : candidate(speedValue, "mm/s", retractionMatch[0]),
        review: "unreviewed",
      };
    }
  }

  const diameterMatch =
    text.match(/(?:diameter|dia\.?|ø)\D{0,12}(1[.,]\d{2}|2[.,]\d{2})\s*mm/i) ??
    text.match(/\b(1[.,]75|2[.,]85)\s*mm\b/i);
  const diameter = diameterMatch
    ? candidate(Number(diameterMatch[1].replace(",", ".")), "mm", diameterMatch[0])
    : null;

  const weightMatch =
    text.match(/(?:net\s*(?:weight|wt\.?)|weight|content)\D{0,14}(\d{1,5}(?:[.,]\d+)?)\s*(kg|g)\b/i) ??
    text.match(/\b(\d(?:[.,]\d+)?)\s*(kg)\b/i);
  const weightGrams = weightMatch
    ? candidate(
        Math.round(
          Number(weightMatch[1].replace(",", ".")) *
            (weightMatch[2].toLowerCase() === "kg" ? 1000 : 1),
        ),
        "g",
        weightMatch[0],
      )
    : null;

  const dryingMatch = text.match(
    /(?:dry(?:ing)?|dehumidif\w*)\D{0,20}(\d{2,3})\s*°?\s*C(?:\D{0,20}?(\d+(?:[.,]\d+)?)\s*(?:h|hr|hrs|hour|hours))?/i,
  );
  const drying = dryingMatch
    ? {
        temperature: candidate(Number(dryingMatch[1]), "°C", dryingMatch[0]),
        duration: dryingMatch[2]
          ? candidate(Number(dryingMatch[2].replace(",", ".")), "h", dryingMatch[0])
          : null,
        review: "unreviewed",
      }
    : null;

  const colorMatches = COLOR_WORDS.filter((word) => new RegExp(`\\b${word}\\b`, "i").test(text));
  const effectMatches = EFFECT_WORDS.filter((word) => new RegExp(`\\b${word}\\b`, "i").test(text));
  const color = colorMatches.length
    ? candidate([...new Set([...colorMatches, ...effectMatches])].join(" "), null, text.match(new RegExp(`\\b${colorMatches[0]}\\b`, "i"))?.[0] ?? colorMatches[0], "vocabulary")
    : null;

  const identifiers = [
    ...new Set(
      (text.match(/\b[A-Z0-9][A-Z0-9._/-]{5,24}\b/g) ?? []).filter(
        (token) => /\d/.test(token) && /[A-Z]/i.test(token),
      ),
    ),
  ]
    .slice(0, 12)
    .map((token) => candidate(token, null, token));

  const gtins = [
    ...new Set((text.match(/\b\d{8}\b|\b\d{12,14}\b/g) ?? []).map((token) => token.trim())),
  ].map((token) => candidate(token, null, token, "checksum_unverified"));

  const brand = parseBrand(text, options.knownBrands ?? []);
  const productName = parseProductName(rawText, brand, family);
  const flame = explicitFlameStatement(text);

  const fields = {
    brand,
    product_name: productName,
    material_family: family,
    color,
    diameter,
    net_weight: weightGrams,
    nozzle_temperature: nozzleTemperature,
    bed_temperature: bedTemperature,
    print_speed: speed,
    cooling_fan: coolingFan,
    flow_ratio: flowRatio,
    max_volumetric_speed: maxVolumetricSpeed,
    retraction,
    drying,
    flame_statement: flame,
    identifiers,
    gtin_candidates: gtins,
  };

  const extractedCount = Object.values(fields).filter((entry) =>
    Array.isArray(entry) ? entry.length : Boolean(entry),
  ).length;

  return {
    schema: "paramat-label-extraction/v2",
    parser_version: "2.1.0",
    source: "label_ocr",
    review: "unreviewed",
    raw_text: rawText.slice(0, 10_000),
    fields,
    extracted_field_groups: extractedCount,
    warnings: [
      "OCR-derived fields require operator verification against the physical label.",
      ...(flame
        ? ["Flame information is retained only as an unverified explicit label statement."]
        : []),
    ],
  };
}
