import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex h-[60vh] flex-col items-center justify-center gap-4 text-center px-4">
      <h1 className="text-6xl font-bold">404</h1>
      <p className="text-xl text-muted-foreground">Page not found</p>
      <Link
        href="/"
        className="mt-4 inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary hover:underline"
      >
        Back to catalog
      </Link>
    </div>
  );
}