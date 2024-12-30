import { useState } from 'react';
import { validateTimeFormat, validateSleepTime, validateTimeSelection } from '../utils/timeUtils';
import { validateTaskDuration } from '../utils/taskUtils';
import { inferNaturalLanguage, generateSchedule } from '@/services/api';
import useScheduleStore from '@/store/scheduleStore';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export const useSchedule = () => {
  const router = useRouter();
  const setSchedule = useScheduleStore((state) => state.setSchedule);
  const [step, setStep] = useState(1);
  const [tempSelection, setTempSelection] = useState('');
  const [isTextInput, setIsTextInput] = useState(false);
  const [timeError, setTimeError] = useState('');
  
  const [tempObligation, setTempObligation] = useState({
    name: '',
    startTime: '',
    endTime: '',
    error: '',
    warning: ''
  });

  const [tempTask, setTempTask] = useState({
    name: '',
    duration: '',
    unit: 'minutes',
    error: '',
    naturalText: '',
    isParsed: false
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

  const handleTimeSelect = (time) => {
    if (isTextInput && !validateTimeFormat(time)) {
      setTimeError("Please enter time in HH:mm format (e.g., 09:00)");
      return;
    }
    
    setTempSelection(time);
    if (step === 2) {
      const error = validateSleepTime(scheduleData.wakeTime, time);
      setTimeError(error);
    } else {
      setTimeError('');
    }
  };

  const confirmTimeSelection = (type) => {
    if (!tempSelection) return;
    if (type === 'sleepTime' && timeError) return;
    
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
    setTimeError('');
  };

  const handleObligationInput = (field, value) => {
    setTempObligation(prev => {
      const newObligation = {
        ...prev,
        [field]: value,
        error: '',
        warning: ''
      };

      if (newObligation.startTime && newObligation.endTime) {
        const validation = validateTimeSelection(
          newObligation.startTime,
          newObligation.endTime,
          scheduleData.wakeTime,
          scheduleData.sleepTime,
          scheduleData.obligations
        );
        newObligation.error = validation.error;
        newObligation.warning = validation.warning;
      }

      return newObligation;
    });
  };

  const confirmObligation = () => {
    if (!tempObligation.name || !tempObligation.startTime || !tempObligation.endTime) return;
    if (tempObligation.error) return;

    setScheduleData(prev => ({
      ...prev,
      obligations: [...prev.obligations, {
        name: tempObligation.name,
        startTime: tempObligation.startTime,
        endTime: tempObligation.endTime
      }]
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
    setTempObligation({ name: '', startTime: '', endTime: '', error: '', warning: '' });
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
    setTempTask(prev => {
      const newTask = {
        ...prev,
        [field]: value,
        error: ''
      };

      if (field === 'naturalText') {
        // Reset parsed state when user types
        newTask.isParsed = false;
        newTask.name = '';
        newTask.duration = '';
        newTask.timeOfDay = '';
      } else if (field === 'duration' || field === 'unit') {
        newTask.error = validateTaskDuration(
          field === 'duration' ? value : prev.duration,
          field === 'unit' ? value : prev.unit,
          scheduleData
        );
      }

      return newTask;
    });
  };

  const handleNaturalLanguageInput = async (text) => {
    if (!text) return;

    try {
      const { parsed_info } = await inferNaturalLanguage(text);
      
      if (parsed_info.task_name && parsed_info.duration) {
        let durationInMinutes;
        if (parsed_info.duration_unit.toLowerCase().includes('hour')) {
          durationInMinutes = parseInt(parsed_info.duration) * 60;
        } else {
          durationInMinutes = parseInt(parsed_info.duration);
        }

        // Validate the duration
        const error = validateTaskDuration(durationInMinutes.toString(), 'minutes', scheduleData);
        
        setTempTask(prev => ({
          ...prev,
          name: parsed_info.task_name,
          duration: durationInMinutes.toString(),
          unit: 'minutes',
          error,
          timeOfDay: parsed_info.time_of_day,
          isParsed: true
        }));

        // Add time of day information to the message if available
        const timeInfo = parsed_info.time_of_day ? ` (${parsed_info.time_of_day})` : '';
        setMessages(prev => [
          ...prev,
          {
            type: 'bot',
            content: `Detected task: "${parsed_info.task_name}" for ${parsed_info.duration} ${parsed_info.duration_unit}${timeInfo}`
          }
        ]);
      }
    } catch (error) {
      console.error('Error processing natural language:', error);
      setTempTask(prev => ({
        ...prev,
        error: 'Failed to process natural language input',
        isParsed: false
      }));
      setMessages(prev => [
        ...prev,
        {
          type: 'bot',
          content: 'Sorry, I had trouble understanding that. Please try rephrasing or use the structured input.'
        }
      ]);
    }
  };

  const confirmTask = () => {
    if (!tempTask.name || !tempTask.duration || tempTask.error) return;

    const durationInMinutes = tempTask.unit === 'hours' 
      ? parseInt(tempTask.duration) * 60 
      : parseInt(tempTask.duration);

    setScheduleData(prev => ({
      ...prev,
      tasks: [...prev.tasks, {
        name: tempTask.name,
        duration: durationInMinutes.toString()
      }]
    }));

    const newMessages = [
      { 
        type: 'user', 
        content: `${tempTask.name} (${tempTask.duration} ${tempTask.unit})` 
      },
      { 
        type: 'bot', 
        content: "Task added! Would you like to add another task or generate your schedule?" 
      }
    ];

    setMessages(prev => [...prev, ...newMessages]);
    setTempTask({
      name: '',
      duration: '',
      unit: 'minutes',
      error: '',
      naturalText: '',
      isParsed: false
    });
  };

  const generateFinalSchedule = async () => {
    try {
      setMessages(prev => [
        ...prev,
        { 
          type: 'bot', 
          content: "Generating your schedule..." 
        }
      ]);

      const result = await generateSchedule(scheduleData);
      setSchedule(result);
      router.push('/timetable');
      
    } catch (error) {
      console.error('Error generating schedule:', error);
      setMessages(prev => [
        ...prev,
        { 
          type: 'bot', 
          content: "Sorry, I couldn't generate the schedule. Please try again." 
        }
      ]);
    }
    setStep(5);
  };

  return {
    step,
    tempSelection,
    isTextInput,
    timeError,
    tempObligation,
    tempTask,
    messages,
    scheduleData,
    handleTimeSelect,
    confirmTimeSelection,
    handleObligationInput,
    confirmObligation,
    moveToTasks,
    handleTaskInput,
    handleNaturalLanguageInput,
    confirmTask,
    generateFinalSchedule,
    setIsTextInput
  };
}; 