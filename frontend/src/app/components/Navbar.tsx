"use client";
import { useRepolensApi } from "../utils/api";

export default function Navbar({ children }: { children?: React.ReactNode }) {
  const { isLocal } = useRepolensApi();

  return (
    <nav className="w-full bg-background border-b border-white/10 text-white px-6 py-4 flex items-center shadow-lg relative z-10">
      <span className="font-bold text-2xl tracking-tight text-primary mr-4">
        RepoLens
      </span>
      <span
        className={
          isLocal
            ? "ml-4 px-3 py-1 rounded-full bg-green-100 text-green-800 text-xs font-semibold"
            : "ml-4 px-3 py-1 rounded-full bg-red-100 text-red-800 text-xs font-semibold"
        }
      >
        {isLocal ? "Connected to Local Agent" : "Agent Not Connected"}
      </span>
      {children}
    </nav>
  );
}
