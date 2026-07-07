import "./globals.css";

export const metadata = {
  title: "ResearchPilot",
  description: "MCP-based academic research assistant",
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
