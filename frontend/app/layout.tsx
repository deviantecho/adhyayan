import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Adhyayan — Class 10 NCERT Study Companion",
  description: "Explore Class 10 NCERT material through chapter-focused conversations.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
