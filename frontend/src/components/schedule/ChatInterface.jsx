import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Check, Plus, ArrowRight } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";

export default function ChatInterface() {
  const [step, setStep] = useState(1);
  const [tempSelection, setTempSelection] = useState('');
  const [tempObligation, setTempObligation] = useState({
    name: '',
    startTime: '',
    endTime: ''
  });
  const [tempTask, setTempTask] = useState({
    name: '',
    duration: ''
  });
  const [messages, setMessages] = useState([
    { type: 'bot', content: "Hi! Let's create your schedule. What time do you usually wake up?" }
  ]);
  const [scheduleData, setScheduleData] = useState({
    wakeTime: '',
    sleepTime: '',
    obligations: [],
    tasks: [],
  });
  
  const timeOptions = Array.from({ length: 24 }, (_, i) => {
    const hour = i.toString().padStart(2, '0');
    return `${hour}:00`;
  });

  const handleTimeSelect = (time) => {
    setTempSelection(time);
  };

  const confirmTimeSelection = (type) => {
    if (!tempSelection) return;
    
    setScheduleData(prev => ({
      ...prev,
      [type]: tempSelection
    }));

    const newMessages = [
      { type: 'user', content: tempSelection },
    ];

    if (type === 'wakeTime') {
      newMessages.push({ 
        type: 'bot', 
        content: "Great! And what time do you usually go to sleep?" 
      });
      setStep(2);
    } else if (type === 'sleepTime') {
      newMessages.push({ 
        type: 'bot', 
        content: "Now, let's add your daily obligations (classes, meetings, etc.). What's your first obligation?" 
      });
      setStep(3);
    }

    setMessages(prev => [...prev, ...newMessages]);
    setTempSelection('');
  };

  const handleObligationInput = (field, value) => {
    setTempObligation(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const confirmObligation = () => {
    if (!tempObligation.name || !tempObligation.startTime || !tempObligation.endTime) return;

    setScheduleData(prev => ({
      ...prev,
      obligations: [...prev.obligations, tempObligation]
    }));

    const newMessages = [
      { 
        type: 'user', 
        content: `${tempObligation.name}: ${tempObligation.startTime} - ${tempObligation.endTime}` 
      },
      { 
        type: 'bot', 
        content: "Obligation added! Would you like to add another obligation or move to tasks?" 
      }
    ];

    setMessages(prev => [...prev, ...newMessages]);
    setTempObligation({ name: '', startTime: '', endTime: '' });
  };

  const moveToTasks = () => {
    setMessages(prev => [
      ...prev,
      { 
        type: 'bot', 
        content: "Great! Now let's add the tasks you want to complete. What's your first task?" 
      }
    ]);
    setStep(4);
  };

  const handleTaskInput = (field, value) => {
    setTempTask(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const confirmTask = () => {
    if (!tempTask.name || !tempTask.duration) return;

    setScheduleData(prev => ({
      ...prev,
      tasks: [...prev.tasks, tempTask]
    }));

    const newMessages = [
      { 
        type: 'user', 
        content: `${tempTask.name} (${tempTask.duration} minutes)` 
      },
      { 
        type: 'bot', 
        content: "Task added! Would you like to add another task or generate your schedule?" 
      }
    ];

    setMessages(prev => [...prev, ...newMessages]);
    setTempTask({ name: '', duration: '' });
  };

  const generateSchedule = () => {
    setMessages(prev => [
      ...prev,
      { 
        type: 'bot', 
        content: "Here's your schedule data! (Schedule generation algorithm to be implemented)" 
      },
      {
        type: 'bot',
        content: <pre className="whitespace-pre-wrap">{JSON.stringify(scheduleData, null, 2)}</pre>
      }
    ]);
    setStep(5);
  };

  const renderTimeSelector = (type) => (
    <div className="flex items-center gap-2">
      <Select onValueChange={(value) => handleTimeSelect(value)}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Select time" />
        </SelectTrigger>
        <SelectContent>
          {timeOptions.map((time) => (
            <SelectItem key={time} value={time}>
              {time}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Button 
        size="icon" 
        disabled={!tempSelection}
        onClick={() => confirmTimeSelection(type)}
      >
        <Check className="h-4 w-4" />
      </Button>
    </div>
  );

  const renderObligationInput = () => (
    <div className="space-y-4">
      <div className="space-y-2">
        <Input
          placeholder="Obligation name"
          value={tempObligation.name}
          onChange={(e) => handleObligationInput('name', e.target.value)}
          className="w-[200px]"
        />
        <div className="flex items-center gap-2">
          <Select onValueChange={(value) => handleObligationInput('startTime', value)}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Start time" />
            </SelectTrigger>
            <SelectContent>
              {timeOptions.map((time) => (
                <SelectItem key={time} value={time}>{time}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select onValueChange={(value) => handleObligationInput('endTime', value)}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="End time" />
            </SelectTrigger>
            <SelectContent>
              {timeOptions.map((time) => (
                <SelectItem key={time} value={time}>{time}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Button 
          className="flex items-center gap-2"
          disabled={!tempObligation.name || !tempObligation.startTime || !tempObligation.endTime}
          onClick={confirmObligation}
        >
          <Plus className="h-4 w-4" />
          Add Obligation
        </Button>
        <Button 
          variant="outline"
          className="flex items-center gap-2"
          onClick={moveToTasks}
        >
          <ArrowRight className="h-4 w-4" />
          Move to Tasks
        </Button>
      </div>
    </div>
  );

  const renderTaskInput = () => (
    <div className="flex items-center gap-2">
      <Input
        placeholder="Task name"
        value={tempTask.name}
        onChange={(e) => handleTaskInput('name', e.target.value)}
        className="w-[200px]"
      />
      <Input
        type="number"
        placeholder="Duration (mins)"
        value={tempTask.duration}
        onChange={(e) => handleTaskInput('duration', e.target.value)}
        className="w-[140px]"
      />
      <Button 
        size="icon"
        disabled={!tempTask.name || !tempTask.duration}
        onClick={confirmTask}
      >
        <Plus className="h-4 w-4" />
      </Button>
      <Button 
        size="icon"
        variant="outline"
        onClick={generateSchedule}
      >
        <ArrowRight className="h-4 w-4" />
      </Button>
    </div>
  );

  const renderCurrentInput = () => {
    switch(step) {
      case 1:
        return renderTimeSelector('wakeTime');
      case 2:
        return renderTimeSelector('sleepTime');
      case 3:
        return renderObligationInput();
      case 4:
        return renderTaskInput();
      default:
        return null;
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto h-[calc(100vh-4rem)]">
      <div className="h-full overflow-y-auto p-6">
        {/* Message History */}
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
          
          {/* Input Section - In message flow */}
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