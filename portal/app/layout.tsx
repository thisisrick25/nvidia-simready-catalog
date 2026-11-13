import type { Metadata } from "next";
import { TooltipProvider } from "@/components/ui/tooltip";
import "./globals.css";
import { Analytics } from '@vercel/analytics/react'
import Script from 'next/script'

export const metadata: Metadata = {
  title: "SimReady Explorer",
  description: "A catalog of NVIDIA SimReady assets and validation results.",
  metadataBase: new URL("https://swapnaneel.me"),
  alternates: {
    canonical: "/projects/nvidia-simready-catalog",
  },

};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
    {/* <!-- Google tag (gtag.js) --> */}
      <Script async src="https://www.googletagmanager.com/gtag/js?id=G-HVS1V1YG5Z"></Script>
      <Script id="google-analytics" strategy="afterInteractive">
        {`window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());

        gtag('config', 'G-HVS1V1YG5Z');`}
      </Script>
      <body>
        <TooltipProvider>{children}</TooltipProvider>
        <Analytics />
      </body>
    </html>
  );
}
