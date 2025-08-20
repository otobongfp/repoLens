import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Link from "next/link";

export default function Home() {
  return (
    <div className="relative min-h-screen bg-background flex flex-col overflow-hidden">
      {/* Blurry shapes background */}
      <div className="absolute inset-0 -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[400px] h-[400px] bg-[#1db470] opacity-30 rounded-full filter blur-3xl" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-400 opacity-20 rounded-full filter blur-2xl" />
        <div className="absolute top-[30%] left-[60%] w-[300px] h-[300px] bg-pink-300 opacity-20 rounded-full filter blur-2xl" />
      </div>
      <Navbar />
      <main className="flex-1 flex flex-col items-center justify-center px-4">
        <Hero />
        <div className="flex justify-center mt-8">
          <Link href="/dashboard/select">
            <button className="px-8 py-3 bg-primary text-white rounded-lg shadow-lg hover:bg-primary/80 transition text-lg font-semibold">
              Get Started
            </button>
          </Link>
        </div>
      </main>
    </div>
  );
}
