'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { TokenSource } from 'livekit-client';
import { useSession, useSessionContext } from '@livekit/components-react';
import { AgentSessionProvider } from '@/components/agents-ui/agent-session-provider';
import { StartAudioButton } from '@/components/agents-ui/start-audio-button';
import { DashboardLayout, type DemoConfig } from '@/components/dashboard/DashboardLayout';
import { useAgentErrors } from '@/hooks/useAgentErrors';

interface DemoDashboardProps {
  config: DemoConfig;
  selectedLanguage: string;
  onLanguageChange: (code: string) => void;
}

/**
 * Inner dashboard — must render inside AgentSessionProvider so LiveKit
 * hooks (useSessionContext, useRoomContext, useVoiceAssistant) are available.
 */
function InnerDemoDashboard({ config, selectedLanguage, onLanguageChange }: DemoDashboardProps) {
  const router = useRouter();
  const { isConnected, start, end } = useSessionContext();

  useAgentErrors();

  // Auto-connect on mount
  useEffect(() => {
    start();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const connectionState = isConnected ? 'connected' : 'connecting';

  const handleReset = () => {
    end();
    router.push('/');
  };

  return (
    <DashboardLayout
      config={config}
      connectionState={connectionState}
      selectedLanguage={selectedLanguage}
      onLanguageChange={onLanguageChange}
      onDisconnect={end}
      onReset={handleReset}
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
        body: JSON.stringify({ language: initialLanguage }),
      });
      if (!res.ok) throw new Error(`Connection details fetch failed: ${res.status}`);
      return res.json();
    });
  }, [initialLanguage]);

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
