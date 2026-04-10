'use client';

import { useMemo, useState } from 'react';
import { useSession } from '@livekit/components-react';
import { WarningIcon } from '@phosphor-icons/react/dist/ssr';
import type { AppConfig } from '@/app-config';
import { AgentSessionProvider } from '@/components/agents-ui/agent-session-provider';
import { StartAudioButton } from '@/components/agents-ui/start-audio-button';
import { ViewController } from '@/components/app/view-controller';
import { Toaster } from '@/components/ui/sonner';
import { useAgentErrors } from '@/hooks/useAgentErrors';
import { useDebugMode } from '@/hooks/useDebug';
import { getEndpointTokenSource } from '@/lib/utils';

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';

function AppSetup() {
  useDebugMode({ enabled: IN_DEVELOPMENT });
  useAgentErrors();

  return null;
}

interface AppProps {
  appConfig: AppConfig;
}

const REALTIME_VOICES = ['Aoede', 'Kore', 'Puck', 'Charon', 'Fenrir'] as const;

export function App({ appConfig }: AppProps) {
  const [selectedVoice, setSelectedVoice] = useState<string>('Aoede');

  const tokenSource = useMemo(() => {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
    const endpointFromEnv = process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT;
    const endpoint = backendUrl
      ? `${backendUrl}/api/connection-details`
      : typeof endpointFromEnv === 'string' && endpointFromEnv.trim().length > 0
        ? endpointFromEnv
        : '/api/connection-details';

    return getEndpointTokenSource(appConfig, endpoint, selectedVoice);
  }, [appConfig, selectedVoice]);

  const session = useSession(
    tokenSource,
    appConfig.agentName ? { agentName: appConfig.agentName } : undefined
  );

  return (
    <AgentSessionProvider session={session}>
      <AppSetup />
      <main className="grid h-svh grid-cols-1 place-content-center">
        <ViewController
          appConfig={appConfig}
          selectedVoice={selectedVoice}
          onSelectedVoiceChange={setSelectedVoice}
          voiceOptions={[...REALTIME_VOICES]}
        />
      </main>
      <StartAudioButton label="Start Audio" />
      <Toaster
        icons={{
          warning: <WarningIcon weight="bold" />,
        }}
        position="top-center"
        className="toaster group"
        style={
          {
            '--normal-bg': 'var(--popover)',
            '--normal-text': 'var(--popover-foreground)',
            '--normal-border': 'var(--border)',
          } as React.CSSProperties
        }
      />
    </AgentSessionProvider>
  );
}
