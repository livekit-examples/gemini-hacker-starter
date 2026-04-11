'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { TokenSource } from 'livekit-client';
import { useRoomContext, useSession, useSessionContext } from '@livekit/components-react';
import { AgentSessionProvider } from '@/components/agents-ui/agent-session-provider';
import { StartAudioButton } from '@/components/agents-ui/start-audio-button';
import { DashboardLayout, type DemoConfig } from '@/components/dashboard/DashboardLayout';
import { useAgentErrors } from '@/hooks/useAgentErrors';

interface DemoDashboardProps {
  config: DemoConfig;
  selectedLanguage: string;
  onLanguageChange: (code: string) => void;
}

interface MicrophoneInfo {
  deviceId: string;
  label: string;
}

/**
 * Inner dashboard — must render inside AgentSessionProvider so LiveKit
 * hooks (useSessionContext, useRoomContext, useVoiceAssistant) are available.
 */
function InnerDemoDashboard({ config, selectedLanguage, onLanguageChange }: DemoDashboardProps) {
  const router = useRouter();
  const room = useRoomContext();
  const { isConnected, start, end } = useSessionContext();
  const [microphones, setMicrophones] = useState<MicrophoneInfo[]>([]);
  const [selectedMicrophoneId, setSelectedMicrophoneId] = useState<string>('');

  useAgentErrors();

  // Auto-connect on mount
  useEffect(() => {
    start();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const mediaDevices = navigator.mediaDevices;
    if (!mediaDevices?.enumerateDevices) {
      return;
    }

    const refreshMicrophones = async () => {
      try {
        const devices = await mediaDevices.enumerateDevices();
        const audioInputs = devices
          .filter((device) => device.kind === 'audioinput')
          .map((device, index) => ({
            deviceId: device.deviceId,
            label: device.label || `Microphone ${index + 1}`,
          }));
        setMicrophones(audioInputs);
      } catch (error) {
        console.error('Failed to enumerate audio input devices', error);
      }
    };

    refreshMicrophones();
    mediaDevices.addEventListener('devicechange', refreshMicrophones);

    return () => {
      mediaDevices.removeEventListener('devicechange', refreshMicrophones);
    };
  }, []);

  const handleMicrophoneChange = async (deviceId: string) => {
    setSelectedMicrophoneId(deviceId);

    if (!isConnected || !deviceId) {
      return;
    }

    try {
      await room.switchActiveDevice('audioinput', deviceId);
    } catch (error) {
      console.error('Failed to switch microphone device', error);
    }
  };

  const [isDisconnected, setIsDisconnected] = useState(false);
  const [toolOutputResetVersion, setToolOutputResetVersion] = useState(0);

  const connectionState = isConnected ? 'connected' : isDisconnected ? 'idle' : 'connecting';

  const handleDisconnect = () => {
    end();
    setIsDisconnected(true);
    setToolOutputResetVersion((prev) => prev + 1);
  };

  const handleConnect = () => {
    setIsDisconnected(false);
    start();
  };

  const handleReset = () => {
    end();
    setToolOutputResetVersion((prev) => prev + 1);
    router.push('/');
  };

  return (
    <DashboardLayout
      config={config}
      connectionState={connectionState}
      selectedLanguage={selectedLanguage}
      onLanguageChange={onLanguageChange}
      microphones={microphones}
      selectedMicrophoneId={selectedMicrophoneId}
      onMicrophoneChange={handleMicrophoneChange}
      onDisconnect={handleDisconnect}
      onConnect={handleConnect}
      onReset={handleReset}
      toolOutputResetVersion={toolOutputResetVersion}
    />
  );
}

interface DemoClientProps {
  config: DemoConfig;
  initialLanguage?: string;
}

export function DemoClient({ config, initialLanguage = 'en' }: DemoClientProps) {
  const [selectedLanguage, setSelectedLanguage] = useState(initialLanguage);

  const tokenSource = useMemo(() => {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL ?? '';
    const endpoint = backendUrl
      ? `${backendUrl}/api/connection-details`
      : '/api/connection-details';

    return TokenSource.custom(async () => {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          language: selectedLanguage,
          industry: config.slug,
          room_config: {
            agents: [{ agent_name: 'gemini-hackathon-agent' }],
          },
        }),
      });
      if (!res.ok) throw new Error(`Connection details fetch failed: ${res.status}`);
      return res.json();
    });
  }, [config.slug, selectedLanguage]);

  const session = useSession(tokenSource);

  return (
    <AgentSessionProvider session={session}>
      <StartAudioButton label="Start Audio" />
      <InnerDemoDashboard
        config={config}
        selectedLanguage={selectedLanguage}
        onLanguageChange={setSelectedLanguage}
      />
    </AgentSessionProvider>
  );
}
