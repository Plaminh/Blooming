const healthUrl =
  process.env.BLOOMING_BACKEND_HEALTH_URL ??
  "http://127.0.0.1:8000/api/v1/health/db";

const timeoutMs = Number(process.env.BLOOMING_BACKEND_STARTUP_TIMEOUT_MS ?? 60_000);
const retryDelayMs = 250;
const requestTimeoutMs = 2_000;

if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
  console.error(
    "[wait-backend] BLOOMING_BACKEND_STARTUP_TIMEOUT_MS must be a positive number."
  );
  process.exit(1);
}

const startedAt = Date.now();

const delay = (milliseconds) =>
  new Promise((resolve) => setTimeout(resolve, milliseconds));

async function isBackendReady() {
  const controller = new AbortController();
  const requestTimer = setTimeout(() => controller.abort(), requestTimeoutMs);

  try {
    const response = await fetch(healthUrl, {
      method: "GET",
      cache: "no-store",
      signal: controller.signal,
    });
    return response.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(requestTimer);
  }
}

async function main() {
  console.log(`[wait-backend] Waiting for ${healthUrl}`);

  while (Date.now() - startedAt < timeoutMs) {
    if (await isBackendReady()) {
      console.log(
        `[wait-backend] API and database are ready after ${Date.now() - startedAt}ms.`
      );
      return;
    }

    await delay(retryDelayMs);
  }

  console.error(
    `[wait-backend] Timed out after ${timeoutMs}ms waiting for ${healthUrl}.`
  );
  process.exitCode = 1;
}

main().catch((error) => {
  console.error("[wait-backend] Unexpected startup check failure:", error);
  process.exitCode = 1;
});
