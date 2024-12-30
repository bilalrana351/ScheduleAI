'use client';

import { Card } from "@/components/ui/card";
import useScheduleStore from "@/store/scheduleStore";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function TimetablePage() {
  const schedule = useScheduleStore((state) => state.schedule);
  const router = useRouter();

  useEffect(() => {
    if (!schedule) {
      router.push('/schedule');
    }
  }, [schedule, router]);

  if (!schedule) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">Redirecting to schedule page...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">Your Schedule</h1>
      
      <div className="grid gap-6">
        {/* Obligations Section */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Fixed Obligations</h2>
          <div className="grid gap-3">
            {schedule.obligations?.map((item, index) => (
              <Card key={index} className="p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-medium">{item.task}</h3>
                  </div>
                  <div className="text-gray-600">
                    {item.start} - {item.end}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Tasks Section */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Scheduled Tasks</h2>
          <div className="grid gap-3">
            {schedule.schedule?.map((item, index) => (
              <Card key={index} className="p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-medium">{item.task}</h3>
                  </div>
                  <div className="text-gray-600">
                    {item.start} - {item.end}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 