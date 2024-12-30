"use client"

import { Clock } from "lucide-react"
import Link from "next/link"
import ChatInterface from "@/components/schedule/ChatInterface"

export default function SchedulePage() {
  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <header className="px-4 lg:px-6 h-16 flex items-center justify-between border-b bg-white">
        <Link className="flex items-center justify-center" href="/">
          <Clock className="h-6 w-6" />
          <span className="ml-2 text-2xl font-bold">ScheduleAI</span>
        </Link>
      </header>
      <main className="flex-1 overflow-hidden">
        <ChatInterface />
      </main>
    </div>
  );
}