import { useState, useEffect } from "react";
import { Mic, Loader2 } from "lucide-react";
import { Button } from "./button";

interface VoiceRecorderProps {
  onTranscriptionComplete: (text: string) => void;
  isHindi?: boolean;
}

export function VoiceRecorder({ onTranscriptionComplete, isHindi = false }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      // @ts-ignore
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const rec = new SpeechRecognition();
        rec.continuous = false;
        rec.interimResults = false;
        
        rec.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          onTranscriptionComplete(transcript);
          setIsRecording(false);
        };
        
        rec.onerror = (event: any) => {
          console.error("Speech recognition error", event.error);
          setIsRecording(false);
        };
        
        rec.onend = () => {
          setIsRecording(false);
        };
        
        setRecognition(rec);
      }
    }
  }, [onTranscriptionComplete]);

  const toggleRecording = () => {
    if (!recognition) {
      alert("Voice recognition is not supported in this browser.");
      return;
    }
    
    if (isRecording) {
      recognition.stop();
      setIsRecording(false);
    } else {
      recognition.lang = isHindi ? 'hi-IN' : 'en-US';
      recognition.start();
      setIsRecording(true);
    }
  };

  return (
    <Button 
      type="button" 
      variant={isRecording ? "destructive" : "outline"} 
      size="icon" 
      onClick={toggleRecording}
      title="Voice Dictation"
    >
      {isRecording ? <Loader2 className="h-4 w-4 animate-spin" /> : <Mic className="h-4 w-4" />}
    </Button>
  );
}
