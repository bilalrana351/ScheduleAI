import { Button } from "@/components/ui/button";
import { Plus, ArrowRight, Edit2 } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Textarea } from "@/components/ui/textarea";

const timeOfDayOptions = [
  "morning",
  "afternoon",
  "evening",
  "night"
];

export function TaskInput({ 
  tempTask,
  isTextInput,
  onTaskInput,
  onNaturalLanguageInput,
  onConfirm,
  onGenerateSchedule
}) {
  const durationOptions = tempTask.unit === 'hours' 
    ? Array.from({ length: 24 }, (_, i) => (i + 1).toString())
    : Array.from({ length: 60 }, (_, i) => (i + 1).toString());

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        {isTextInput ? (
          <>
            <Textarea
              placeholder="Describe your task (e.g., 'Read book for 2 hours in the morning')"
              value={tempTask.naturalText || ''}
              onChange={(e) => {
                const text = e.target.value;
                onTaskInput('naturalText', text);
              }}
              className="w-full min-h-[100px] resize-none"
            />
            {tempTask.showForm && (
              <div className="bg-gray-50 p-4 rounded-lg space-y-3 border">
                <h3 className="font-medium text-sm text-gray-700">
                  {tempTask.isParsed ? "Detected Information" : "Enter Task Details"}
                </h3>
                <div className="space-y-3">
                  {/* Task Name */}
                  <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Task Name</label>
                    <Input
                      value={tempTask.name || ''}
                      onChange={(e) => onTaskInput('name', e.target.value)}
                      placeholder="Task name"
                      className="w-full"
                    />
                  </div>

                  {/* Duration and Unit */}
                  <div className="grid grid-cols-2 gap-2">
                    <div className="space-y-1">
                      <label className="text-sm font-medium text-gray-600">Duration</label>
                      <Select 
                        value={tempTask.duration || ''} 
                        onValueChange={(value) => onTaskInput('duration', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Duration" />
                        </SelectTrigger>
                        <SelectContent>
                          {durationOptions.map((duration) => (
                            <SelectItem key={duration} value={duration}>
                              {duration}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <label className="text-sm font-medium text-gray-600">Unit</label>
                      <Select 
                        value={tempTask.unit} 
                        onValueChange={(value) => onTaskInput('unit', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Unit" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="minutes">Minutes</SelectItem>
                          <SelectItem value="hours">Hours</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {/* Time of Day */}
                  <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Time of Day (Optional)</label>
                    <Select 
                      value={tempTask.timeOfDay || ''} 
                      onValueChange={(value) => onTaskInput('timeOfDay', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select preferred time" />
                      </SelectTrigger>
                      <SelectContent>
                        {timeOfDayOptions.map((time) => (
                          <SelectItem key={time} value={time}>
                            {time.charAt(0).toUpperCase() + time.slice(1)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          <>
            <Input
              placeholder="Task name"
              value={tempTask.name}
              onChange={(e) => onTaskInput('name', e.target.value)}
              className="w-[200px]"
            />
            <div className="flex items-center gap-2">
              <Select value={tempTask.duration} onValueChange={(value) => onTaskInput('duration', value)}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="Duration" />
                </SelectTrigger>
                <SelectContent>
                  {durationOptions.map((duration) => (
                    <SelectItem key={duration} value={duration}>
                      {duration}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={tempTask.unit} onValueChange={(value) => onTaskInput('unit', value)}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="Unit" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="minutes">Minutes</SelectItem>
                  <SelectItem value="hours">Hours</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </>
        )}
        {tempTask.error && (
          <Alert variant="destructive" className="mt-2">
            <AlertDescription>
              {tempTask.error}
            </AlertDescription>
          </Alert>
        )}
      </div>
      <div className="flex items-center gap-2">
        {isTextInput ? (
          <>
            <Button 
              className="flex items-center gap-2"
              disabled={!tempTask.naturalText}
              onClick={() => onNaturalLanguageInput(tempTask.naturalText)}
            >
              <ArrowRight className="h-4 w-4" />
              Next
            </Button>
            {tempTask.showForm && (
              <Button 
                className="flex items-center gap-2"
                onClick={onConfirm}
                disabled={!tempTask.name || !tempTask.duration}
              >
                <Plus className="h-4 w-4" />
                Add Task
              </Button>
            )}
          </>
        ) : (
          <>
            <Button 
              className="flex items-center gap-2"
              disabled={!tempTask.name || !tempTask.duration || tempTask.error}
              onClick={onConfirm}
            >
              <Plus className="h-4 w-4" />
              Add Task
            </Button>
          </>
        )}
        {(!isTextInput || (isTextInput && tempTask.showForm)) && (
          <div className="flex items-center gap-2">
            <Select 
              defaultValue="ac3"
              onValueChange={(value) => onTaskInput('algorithm', value)}
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
              className="flex items-center gap-2"
              onClick={onGenerateSchedule}
            >
              <ArrowRight className="h-4 w-4" />
              Generate Schedule
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}