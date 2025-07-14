export default function Navbar({ children }: { children?: React.ReactNode }) {
  return (
    <nav className="w-full bg-background border-b border-white/10 text-white px-6 py-4 flex items-center shadow-lg relative z-10">
      <span className="font-bold text-2xl tracking-tight text-primary mr-4">
        RepoLens
      </span>
      {children}
    </nav>
  );
}
