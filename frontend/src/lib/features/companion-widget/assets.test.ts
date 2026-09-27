import { render } from "@testing-library/svelte";
import { describe, expect, it } from "vitest";
import CompanionWidget from "./components/organisms/CompanionWidget.svelte";
import { behindScheduleFixture, offlineFixture, pausedFixture, remindersFixture } from "./fixtures";

// Whole frontend source tree, not just this feature folder.
const sources = import.meta.glob("../../../**/*.{ts,js,svelte,css}", {
  query: "?raw",
  eager: true,
  import: "default",
}) as Record<string, string>;

const FORBIDDEN_IMAGE_REFERENCE_PATTERNS = [
  /\$lib\/assets/,
  /src\/lib\/assets/,
  /\.\.\/.*\.(?:png|jpe?g|webp|svg|gif)/i,
  /new URL\([^)]*\.(?:png|jpe?g|webp|svg|gif)/i,
];

describe("source-only asset exclusion", () => {
  it("covers the frontend source tree beyond the companion-widget folder", () => {
    const paths = Object.keys(sources);
    expect(paths.length).toBeGreaterThan(0);
    expect(paths.some((path) => !path.includes("companion-widget"))).toBe(true);
  });

  it("uses only root-relative runtime image references from application source", () => {
    const hits: string[] = [];

    for (const [path, source] of Object.entries(sources)) {
      if (path.endsWith(".test.ts")) continue;
      for (const pattern of FORBIDDEN_IMAGE_REFERENCE_PATTERNS) {
        if (pattern.test(source)) {
          hits.push(`${path} matches ${pattern}`);
        }
      }
    }

    expect(hits).toEqual([]);
  });

  it("never embeds base64 images in application source", () => {
    const hits = Object.entries(sources)
      .filter(([path]) => !path.endsWith(".test.ts"))
      .filter(([, source]) => source.includes("data:image"))
      .map(([path]) => path);

    expect(hits).toEqual([]);
  });

  it("contains no retired leaf-balance surface or 384px character-cell metadata", () => {
    const retired = ["LeafBalance", "LeafLogo", "leafBalance", "cellWidth: 384"];
    const hits = Object.entries(sources)
      .filter(([path]) => !path.endsWith(".test.ts"))
      .flatMap(([path, source]) =>
        retired.filter((token) => source.includes(token)).map((token) => `${path}: ${token}`),
      );

    expect(hits).toEqual([]);
  });

  it("requests only runtime asset URLs from every rendered state", () => {
    for (const presentation of [
      pausedFixture,
      behindScheduleFixture,
      offlineFixture,
      remindersFixture,
    ]) {
      const { container, unmount } = render(CompanionWidget, { props: { presentation } });
      const urls = [
        ...[...container.querySelectorAll("img")].map((img) => img.getAttribute("src") ?? ""),
        ...[...container.querySelectorAll("[style]")].map((el) => el.getAttribute("style") ?? ""),
      ];

      for (const url of urls) {
        expect(url.startsWith("data:image")).toBe(false);
      }

      const imageSources = [...container.querySelectorAll("img")].map((img) => img.src);
      expect(imageSources.length).toBeGreaterThan(0);
      for (const src of imageSources) {
        expect(
          src.includes("/assets/mr-bloom/") ||
          src.includes("/assets/plants/") ||
          src.includes("/assets/icons/leaf-icon.png") ||
          src.includes("/assets/widget/environment/"),
        ).toBe(true);
      }
      unmount();
    }
  });
});
