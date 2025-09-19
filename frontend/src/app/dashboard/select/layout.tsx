export const metadata = {
  title: 'Repolens Features',
  description: 'Select a how you want to explore code with RepoLens',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div>{children}</div>;
}
