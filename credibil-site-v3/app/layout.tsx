import type { Metadata } from "next";
import "@fontsource-variable/manrope";
import "./globals.css";

export const metadata: Metadata = {
  title: "Credibil - Verificarea companiilor și partenerilor din Moldova",
  description:
    "Verificați companii și persoane asociate după denumire, IDNO sau nume. Analizați date, legături, rapoarte și schimbări disponibile în Moldova.",
  other: {
    "codex-preview": "development",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
  openGraph: {
    type: "website",
    locale: "ro_MD",
    title: "Credibil - Date pentru verificarea partenerilor din Moldova",
    description:
      "Găsiți o companie sau o persoană, analizați datele de înregistrare și legăturile, generați un raport sau activați monitorizarea.",
    images: [
      {
        url: "/assets/credibil-og.png",
        width: 1200,
        height: 630,
        alt: "Credibil",
      },
    ],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ro">
      <body>{children}</body>
    </html>
  );
}
