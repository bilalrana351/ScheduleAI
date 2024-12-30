import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";

const timeOptions = Array.from({ length: 24 }, (_, i) => {
  const hour = i.toString().padStart(2, '0');
  return `${hour}:00`;
});

export function TimeSelector({ type, tempSelection, timeError, onTimeSelect, onConfirm }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Select onValueChange={onTimeSelect}>
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
          disabled={!tempSelection || (type === 'sleepTime' && timeError)}
          onClick={() => onConfirm(type)}
        >
          <Check className="h-4 w-4" />
        </Button>
      </div>
      {timeError && (
        <Alert variant="destructive">
          <AlertDescription>
            {timeError}
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
} 