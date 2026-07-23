/* ParaMat3D "Enhanced read" (testing) — PP-OCRv4 text detection + recognition
   (PaddleOCR models, Apache-2.0, Baidu) running fully ON-DEVICE via ONNX Runtime
   Web (WASM). The models download TO the device once (~16 MB, browser-cached);
   the photo NEVER leaves the phone. Exposes window.enhancedOcr(canvas, onmsg). */
(function () {
  const ORT_CDN = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.19.2/dist/";
  const BASE = document.currentScript && document.currentScript.src
    ? new URL(".", document.currentScript.src).href : "";
  const M = { det: BASE + "models/ppocrv4_det.onnx", rec: BASE + "models/ppocrv4_rec.onnx", dict: BASE + "models/ppocrv4_dict.txt" };
  let sessP = null;

  function loadOrt(onmsg) {
    if (window.ort) return Promise.resolve();
    onmsg("Loading engine…");
    return new Promise((res, rej) => {
      const s = document.createElement("script");
      s.src = ORT_CDN + "ort.min.js";
      s.onload = () => { ort.env.wasm.wasmPaths = ORT_CDN; res(); };
      s.onerror = () => rej(new Error("engine load failed"));
      document.head.appendChild(s);
    });
  }
  async function sessions(onmsg) {
    if (sessP) return sessP;
    sessP = (async () => {
      await loadOrt(onmsg);
      onmsg("Downloading reading model (≈16 MB, one-time — it stays on your device)…");
      const [detB, recB, dictT] = await Promise.all([
        fetch(M.det).then(r => { if (!r.ok) throw new Error("det model"); return r.arrayBuffer(); }),
        fetch(M.rec).then(r => { if (!r.ok) throw new Error("rec model"); return r.arrayBuffer(); }),
        fetch(M.dict).then(r => { if (!r.ok) throw new Error("dict"); return r.text(); }),
      ]);
      onmsg("Preparing engine…");
      const opt = { executionProviders: ["wasm"] };
      const det = await ort.InferenceSession.create(detB, opt);
      const rec = await ort.InferenceSession.create(recB, opt);
      const dict = dictT.replace(/\r/g, "").split("\n");
      return { det, rec, dict };
    })().catch(e => { sessP = null; throw e; });
    return sessP;
  }

  function toTensor(canvas, mean, std) {
    const w = canvas.width, h = canvas.height;
    const d = canvas.getContext("2d").getImageData(0, 0, w, h).data;
    const out = new Float32Array(3 * h * w);
    for (let i = 0, p = 0; i < h * w; i++, p += 4) {
      out[i] = ((d[p] / 255) - mean[0]) / std[0];
      out[i + h * w] = ((d[p + 1] / 255) - mean[1]) / std[1];
      out[i + 2 * h * w] = ((d[p + 2] / 255) - mean[2]) / std[2];
    }
    return new ort.Tensor("float32", out, [1, 3, h, w]);
  }
  function sized(src, w, h) {
    const c = document.createElement("canvas"); c.width = w; c.height = h;
    const x = c.getContext("2d"); x.imageSmoothingQuality = "high";
    x.drawImage(src, 0, 0, w, h); return c;
  }
  // DB postprocess: threshold -> connected components -> padded axis-aligned boxes.
  function dbBoxes(prob, W, H) {
    const THRESH = 0.3, BOX_THRESH = 0.5, MIN = 3, UNCLIP = 1.6;
    const raw = new Uint8Array(W * H);
    for (let i = 0; i < W * H; i++) raw[i] = prob[i] > THRESH ? 1 : 0;
    // 3x3 dilation: DB predicts shrunk text kernels — merge near-fragments
    // (spaced/stylized lettering) into one component before labeling.
    const bin = new Uint8Array(W * H);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const i = y * W + x;
      if (raw[i] || (x > 0 && raw[i - 1]) || (x < W - 1 && raw[i + 1]) ||
          (y > 0 && raw[i - W]) || (y < H - 1 && raw[i + W])) bin[i] = 1;
    }
    const seen = new Uint8Array(W * H), stack = new Int32Array(W * H), boxes = [];
    for (let s0 = 0; s0 < W * H; s0++) {
      if (!bin[s0] || seen[s0]) continue;
      let sp = 0; stack[sp++] = s0; seen[s0] = 1;
      let minx = W, maxx = 0, miny = H, maxy = 0, sum = 0, cnt = 0;
      while (sp) {
        const idx = stack[--sp], y = (idx / W) | 0, x = idx - y * W;
        if (x < minx) minx = x; if (x > maxx) maxx = x;
        if (y < miny) miny = y; if (y > maxy) maxy = y;
        sum += prob[idx]; cnt++;
        if (x > 0 && bin[idx - 1] && !seen[idx - 1]) { seen[idx - 1] = 1; stack[sp++] = idx - 1; }
        if (x < W - 1 && bin[idx + 1] && !seen[idx + 1]) { seen[idx + 1] = 1; stack[sp++] = idx + 1; }
        if (y > 0 && bin[idx - W] && !seen[idx - W]) { seen[idx - W] = 1; stack[sp++] = idx - W; }
        if (y < H - 1 && bin[idx + W] && !seen[idx + W]) { seen[idx + W] = 1; stack[sp++] = idx + W; }
      }
      const bw = maxx - minx + 1, bh = maxy - miny + 1;
      if (bw < MIN || bh < MIN || sum / cnt < BOX_THRESH) continue;
      const pad = Math.round((bw * bh * UNCLIP) / (2 * (bw + bh)));
      boxes.push({ x0: Math.max(0, minx - pad), y0: Math.max(0, miny - pad),
        x1: Math.min(W - 1, maxx + pad), y1: Math.min(H - 1, maxy + pad) });
    }
    boxes.sort((a, b) => ((a.y0 + a.y1) - (b.y0 + b.y1)) || ((a.x0 + a.x1) - (b.x0 + b.x1)));
    return boxes;
  }
  // CTC: class 0 = blank, 1..dictLen = dict chars, last = space.
  function ctc(logits, T, C, dict) {
    let out = "", last = -1;
    for (let t = 0; t < T; t++) {
      let bi = 0, bv = -1; const off = t * C;
      for (let c = 0; c < C; c++) { const v = logits[off + c]; if (v > bv) { bv = v; bi = c; } }
      if (bi !== 0 && bi !== last) out += bi <= dict.length ? (dict[bi - 1] || "") : " ";
      last = bi;
    }
    return out;
  }

  window.enhancedOcr = async function (canvas, onmsg) {
    onmsg = onmsg || (() => {});
    const { det, rec, dict } = await sessions(onmsg);
    onmsg("Reading…");
    // Match RapidOCR's sizing: SHORT side -> 736 (upscaling small images too),
    // long side capped at 1920 for WASM memory.
    let k = 736 / Math.min(canvas.width, canvas.height);
    if (Math.max(canvas.width, canvas.height) * k > 1920) k = 1920 / Math.max(canvas.width, canvas.height);
    const dw = Math.max(32, Math.round(canvas.width * k / 32) * 32);
    const dh = Math.max(32, Math.round(canvas.height * k / 32) * 32);
    const dout = await det.run({ x: toTensor(sized(canvas, dw, dh), [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]) });
    const prob = dout[Object.keys(dout)[0]].data;
    const boxes = dbBoxes(prob, dw, dh);
    const sx = canvas.width / dw, sy = canvas.height / dh;
    const texts = [];
    for (const b of boxes.slice(0, 40)) {
      const x = Math.round(b.x0 * sx), y = Math.round(b.y0 * sy);
      const w = Math.round((b.x1 - b.x0 + 1) * sx), h = Math.round((b.y1 - b.y0 + 1) * sy);
      if (w < 4 || h < 4) continue;
      const rw = Math.max(16, Math.min(640, Math.round(48 * w / h)));
      const rc = document.createElement("canvas"); rc.width = rw; rc.height = 48;
      const rx = rc.getContext("2d"); rx.imageSmoothingQuality = "high";
      rx.drawImage(canvas, x, y, w, h, 0, 0, rw, 48);
      const ro = await rec.run({ x: toTensor(rc, [0.5, 0.5, 0.5], [0.5, 0.5, 0.5]) });
      const o = ro[Object.keys(ro)[0]];
      const s = ctc(o.data, o.dims[1], o.dims[2], dict).trim();
      if (s) texts.push(s);
    }
    return texts.join("\n");
  };
})();
