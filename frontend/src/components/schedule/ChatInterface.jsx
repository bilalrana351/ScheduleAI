'use client';

import { useSchedule } from './hooks/useSchedule';
import { TimeSelector } from './components/TimeSelector';
import { ObligationInput } from './components/ObligationInput';
import { TaskInput } from './components/TaskInput';
import { Button } from "@/components/ui/button";
import { ArrowUpDown } from "lucide-react";

export default function ChatInterface() {
  const {
    step,
    tempSelection,
    isTextInput,
    timeError,
    tempObligation,
    tempTask,
    messages,
    handleTimeSelect,
    confirmTimeSelection,
    handleObligationInput,
    confirmObligation,
    moveToTasks,
    handleTaskInput,
    handleNaturalLanguageInput,
    confirmTask,
    generateFinalSchedule,
    setIsTextInput,
    scheduleData
  } = useSchedule();

  const renderInputToggle = () => (
    <Button
      variant="outline"
      size="sm"
      onClick={() => setIsTextInput(!isTextInput)}
      className="mb-2"
    >
      <ArrowUpDown className="h-4 w-4 mr-2" />
      Switch to {isTextInput ? 'Structured' : 'Natural Language'} Input
    </Button>
  );

  const renderCurrentInput = () => {
    switch(step) {
      case 1:
        return (
          <TimeSelector
            type="wakeTime"
            tempSelection={tempSelection}
            timeError={timeError}
            onTimeSelect={handleTimeSelect}
            onConfirm={confirmTimeSelection}
          />
        );
      case 2:
        return (
          <TimeSelector
            type="sleepTime"
            tempSelection={tempSelection}
            timeError={timeError}
            onTimeSelect={handleTimeSelect}
            onConfirm={confirmTimeSelection}
          />
        );
      case 3:
        return (
          <ObligationInput
            tempObligation={tempObligation}
            onObligationInput={handleObligationInput}
            onConfirm={confirmObligation}
            onMoveToTasks={moveToTasks}
          />
        );
      case 4:
        return (
          <>
            {renderInputToggle()}
            <TaskInput
              tempTask={tempTask}
              isTextInput={isTextInput}
              onTaskInput={handleTaskInput}
              onNaturalLanguageInput={handleNaturalLanguageInput}
              onConfirm={confirmTask}
              onGenerateSchedule={generateFinalSchedule}
              scheduleData={scheduleData}
            />
          </>
        );
      default:
        return null;
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto h-[calc(100vh-4rem)]">
      <div className="h-full overflow-y-auto p-6">
        <div className="space-y-6">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.type === 'bot' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[600px] rounded-lg p-6 ${
                  message.type === 'bot'
                    ? 'bg-black text-white ml-auto'
                    : 'bg-white border border-gray-200 shadow-sm'
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}
          
          <div className="flex justify-start">
            <div className="max-w-[600px] rounded-lg p-6 bg-white border border-gray-200 shadow-sm">
              {renderCurrentInput()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 