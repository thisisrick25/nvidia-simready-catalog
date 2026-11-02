# Website Integration Snippets

## Iframe Embed (Gradio Portal)

Drop this into any page to embed the live interactive dashboard:

```html
<iframe
  src="https://huggingface.co/spaces/thisisrick25/nvidia-simready-catalog"
  frameborder="0"
  width="100%"
  height="800"
  title="SimReady Assets Explorer"
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope"
  loading="lazy"
></iframe>
```

## Project Links Section

```html
<div class="simready-links">
  <a href="https://github.com/thisisrick25/nvidia-simready-catalog">GitHub</a>
  <a href="https://huggingface.co/datasets/thisisrick25/nvidia-simready-catalog">HF Dataset</a>
  <a href="https://huggingface.co/spaces/thisisrick25/nvidia-simready-catalog">HF Portal</a>
</div>
```

## Next.js "Last Updated" Indicator

Fetch `stats.json` at build time to show when the catalog was last regenerated:

```tsx
// In getStaticProps or a server component
const STATS_URL =
  "https://huggingface.co/datasets/thisisrick25/nvidia-simready-catalog/resolve/main/stats.json";

export async function getStaticProps() {
  const res = await fetch(STATS_URL);
  const stats = await res.json();
  return {
    props: { lastUpdated: stats.as_of, assetCount: stats.n_assets },
    revalidate: 86400, // re-fetch daily
  };
}

// In your component
function CatalogBadge({ lastUpdated, assetCount }) {
  return (
    <span>
      {assetCount} assets &middot; Updated {lastUpdated}
    </span>
  );
}
```

For App Router (React Server Component):

```tsx
const STATS_URL =
  "https://huggingface.co/datasets/thisisrick25/nvidia-simready-catalog/resolve/main/stats.json";

export default async function CatalogBadge() {
  const stats = await fetch(STATS_URL, { next: { revalidate: 86400 } }).then(
    (r) => r.json()
  );
  return (
    <span>
      {stats.n_assets} assets &middot; Updated {stats.as_of}
    </span>
  );
}
```
