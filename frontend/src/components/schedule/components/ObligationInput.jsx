import { Button } from "@/components/ui/button";
import { Plus, ArrowRight } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription } from "@/components/ui/alert";

const timeOptions = Array.from({ length: 24 }, (_, i) => {
  const hour = i.toString().padStart(2, '0');
  return `${hour}:00`;
});

export function ObligationInput({ 
  tempObligation, 
  onObligationInput, 
  onConfirm, 
  onMoveToTasks 
}) {
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Input
          placeholder="Obligation name"
          value={tempObligation.name}
          onChange={(e) => onObligationInput('name', e.target.value)}
          className="w-[200px]"
        />
        <div className="flex items-center gap-2">
          <Select onValueChange={(value) => onObligationInput('startTime', value)}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Start time" />
            </SelectTrigger>
            <SelectContent>
              {timeOptions.map((time) => (
                <SelectItem key={time} value={time}>{time}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select onValueChange={(value) => onObligationInput('endTime', value)}>
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
        {tempObligation.error && (
          <Alert variant="destructive" className="mt-2">
            <AlertDescription>
              {tempObligation.error}
            </AlertDescription>
          </Alert>
        )}
        {tempObligation.warning && !tempObligation.error && (
          <Alert variant="warning" className="mt-2">
            <AlertDescription>
              {tempObligation.warning}
            </AlertDescription>
          </Alert>
        )}
      </div>
      <div className="flex items-center gap-2">
        <Button 
          className="flex items-center gap-2"
          disabled={!tempObligation.name || !tempObligation.startTime || !tempObligation.endTime || tempObligation.error}
          onClick={onConfirm}
        >
          <Plus className="h-4 w-4" />
          Add Obligation
        </Button>
        <Button 
          variant="outline"
          className="flex items-center gap-2"
          onClick={onMoveToTasks}
          disabled={tempObligation.error ? true : false}
        >
          <ArrowRight className="h-4 w-4" />
          Move to Tasks
        </Button>
      </div>
    </div>
  );
} 