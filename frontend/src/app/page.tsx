import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <main className="flex-1 flex flex-col items-center justify-center px-4">
        <Hero />
        <div className="flex justify-center mt-8">
          <Link href="/app">
            <button className="px-8 py-3 bg-primary text-white rounded-lg shadow-lg hover:bg-primary/80 transition text-lg font-semibold">
              Get Started
            </button>
          </Link>
        </div>
      </main>
    </div>
  );
}
