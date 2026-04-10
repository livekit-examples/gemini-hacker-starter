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
}

/**
 * Inner dashboard — must render inside AgentSessionProvider so LiveKit
 * hooks (useSessionContext, useRoomContext, useVoiceAssistant) are available.
 */
function InnerDemoDashboard({ config }: DemoDashboardProps) {
  const router = useRouter();
  const [selectedLanguage, setSelectedLanguage] = useState('en');
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
      onLanguageChange={setSelectedLanguage}
      onDisconnect={end}
      onReset={handleReset}
    />
  );
}

interface DemoClientProps {
  config: DemoConfig;
}

export function DemoClient({ config }: DemoClientProps) {
  const tokenSource = useMemo(() => {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL ?? '';
    const endpoint = backendUrl
      ? `${backendUrl}/api/connection-details`
      : '/api/connection-details';

    return TokenSource.custom(async () => {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      if (!res.ok) throw new Error(`Connection details fetch failed: ${res.status}`);
      return res.json();
    });
  }, []);

  const session = useSession(tokenSource);

  return (
    <AgentSessionProvider session={session}>
      <StartAudioButton label="Start Audio" />
      <InnerDemoDashboard config={config} />
    </AgentSessionProvider>
  );
}
