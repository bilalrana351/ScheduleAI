'use client';

import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import useScheduleStore from "@/store/scheduleStore";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { generateSchedule } from "@/services/api";

export default function TimetablePage() {
  const schedule = useScheduleStore((state) => state.schedule);
  const setSchedule = useScheduleStore((state) => state.setSchedule);
  const scheduleData = useScheduleStore((state) => state.scheduleData);
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('ac3');

  useEffect(() => {
    if (!schedule) {
      router.push('/schedule');
    }
  }, [schedule, router]);

  const handleGenerateSchedule = async () => {
    try {
      setIsLoading(true);
      setError('');
      const result = await generateSchedule(scheduleData, selectedAlgorithm);
      setSchedule(result);
    } catch (error) {
      setError('Failed to generate schedule with the selected algorithm');
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!schedule) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">Redirecting to schedule page...</div>
      </div>
    );
  }

  if (!schedule.found_schedule) {
    return (
      <div className="container mx-auto py-8">
        <h1 className="text-2xl font-bold mb-6">Schedule Generation Status</h1>
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>
            I couldn't find a valid schedule that fits all your tasks within the available time slots. 
            Please try reducing task durations or removing some tasks.
          </AlertDescription>
        </Alert>

        {/* Display Obligations Section */}
        {schedule.obligations && schedule.obligations.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold mb-4">Your Fixed Obligations</h2>
            <div className="grid gap-3">
              {schedule.obligations.map((item, index) => (
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
        )}

        <div className="flex items-center gap-4 mt-6">
          <Select 
            value={selectedAlgorithm}
            onValueChange={setSelectedAlgorithm}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select algorithm" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ac3">AC3</SelectItem>
              <SelectItem value="forward_check">Forward Check</SelectItem>
              <SelectItem value="backtrack">Backtrack</SelectItem>
              <SelectItem value="greedy">Greedy</SelectItem>
            </SelectContent>
          </Select>
          <Button 
            variant="outline"
            onClick={handleGenerateSchedule}
            disabled={isLoading}
          >
            Try Again
          </Button>
          <Button onClick={() => router.push('/schedule')}>
            Back to Schedule
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Your Schedule</h1>
        <div className="flex items-center gap-4">
          <Select 
            value={selectedAlgorithm}
            onValueChange={setSelectedAlgorithm}
            disabled={isLoading}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select algorithm" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ac3">AC3</SelectItem>
              <SelectItem value="forward_check">Forward Check</SelectItem>
              <SelectItem value="backtrack">Backtrack</SelectItem>
              <SelectItem value="greedy">Greedy</SelectItem>
            </SelectContent>
          </Select>
          <Button 
            variant="outline"
            onClick={handleGenerateSchedule}
            disabled={isLoading}
          >
            Try Again
          </Button>
          <Button onClick={() => router.push('/schedule')}>
            Back to Schedule
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {schedule.alternative_scheduler_used && (
        <Alert className="mb-6">
          <AlertDescription>
            The algorithm could not return a valid assignment! Here's an alternate (but less sophisticated) schedule.
          </AlertDescription>
        </Alert>
      )}

      {isLoading ? (
        <div className="text-center py-4">Generating new schedule...</div>
      ) : (
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
      )}
    </div>
  );
} 