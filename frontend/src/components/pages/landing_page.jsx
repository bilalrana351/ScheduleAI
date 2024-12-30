"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Calendar, Clock, MessageSquare } from 'lucide-react'
import Link from "next/link"
import { useRouter } from 'next/navigation'

export default function LandingPage() {
  const router = useRouter();

  const handleGetStarted = () => {
    router.push('/schedule');
  };

  return (
    <div className="flex flex-col min-h-screen">
      <header className="px-4 lg:px-6 h-14 flex items-center">
        <Link className="flex items-center justify-center" href="#">
          <Clock className="h-6 w-6" />
          <span className="ml-2 text-2xl font-bold">ScheduleAI</span>
        </Link>
      </header>
      <main className="flex-1">
        <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none">
                  Make Your Day Productive with AI-Powered Scheduling
                </h1>
                <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
                  ScheduleAI creates personalized timetables using artificial intelligence, helping you optimize your day and boost productivity.
                </p>
              </div>
              <div className="space-x-4">
                <Button onClick={handleGetStarted}>Get Started</Button>
              </div>
            </div>
          </div>
        </section>
        <section className="w-full py-12 md:py-24 lg:py-32 bg-gray-100 dark:bg-gray-800">
          <div className="container px-4 md:px-6">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-center mb-8">
              Key Features
            </h2>
            <div className="grid gap-10 sm:grid-cols-2 md:grid-cols-3">
              <div className="flex flex-col items-center space-y-2 border-gray-800 p-4 rounded-lg">
                <Calendar className="h-12 w-12 mb-2 text-primary" />
                <h3 className="text-xl font-bold">Automatic Task Scheduling</h3>
                <p className="text-gray-500 dark:text-gray-400 text-center">
                  Our AI algorithm optimizes your tasks and creates the perfect schedule for maximum productivity.
                </p>
              </div>
              <div className="flex flex-col items-center space-y-2 border-gray-800 p-4 rounded-lg">
                <MessageSquare className="h-12 w-12 mb-2 text-primary" />
                <h3 className="text-xl font-bold">Natural Language Inputs</h3>
                <p className="text-gray-500 dark:text-gray-400 text-center">
                  Simply tell ScheduleAI what you need to do, and it will understand and organize your tasks.
                </p>
              </div>
              <div className="flex flex-col items-center space-y-2 border-gray-800 p-4 rounded-lg">
                <Clock className="h-12 w-12 mb-2 text-primary" />
                <h3 className="text-xl font-bold">Make Your Day Productive</h3>
                <p className="text-gray-500 dark:text-gray-400 text-center">
                  Optimize your time and achieve more with intelligent scheduling that adapts to your needs.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

