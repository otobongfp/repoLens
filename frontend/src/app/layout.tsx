import "../../styles/globals.css";
import { ApiProvider } from "./context/ApiProvider";

export const metadata = {
  title: "Repolens",
  description: "Improving opensource education with AI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body suppressHydrationWarning={true}>
        <ApiProvider>{children}</ApiProvider>
      </body>
    </html>
  );
}
