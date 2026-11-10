import { PHOTOS } from "../../src/bloglab-open-photos.js";
let failures = 0;
for (const [name, photo] of Object.entries(PHOTOS)) {
  try {
    const response = await fetch(photo.src, {
      headers: { "User-Agent": "BlogLabMediaQA/1.0 (+https://bloglab.eu; check open-license photo links)" },
      signal: AbortSignal.timeout(14000)
    });
    const type = response.headers.get("content-type") || "";
    if (!response.ok || !type.startsWith("image/")) {
      failures++;
      console.log(name, "UNAVAILABLE", response.status, type, response.url);
    } else {
      console.log(name, "IMAGE_OK", response.status, type, response.url);
    }
    await response.body?.cancel?.();
  } catch (error) {
    failures++;
    console.log(name, "NETWORK_ERROR", error.name);
  }
}
if (failures) {
  console.warn("Remote Wikimedia photo probe has", failures, "failures. Check image URLs or third-party rate limits before release.");
  process.exitCode = 1;
}
