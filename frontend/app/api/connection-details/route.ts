import { NextResponse } from 'next/server';
import { AccessToken, type AccessTokenOptions, type VideoGrant } from 'livekit-server-sdk';
import { RoomConfiguration } from '@livekit/protocol';

type ConnectionDetails = {
  serverUrl: string;
  roomName: string;
  participantName: string;
  participantToken: string;
};

const ALLOWED_REALTIME_VOICES = new Set(['Aoede', 'Kore', 'Puck', 'Charon', 'Fenrir']);
const FALLBACK_AGENT_NAME = 'gemini-hackathon-agent';

// NOTE: you are expected to define the following environment variables in `.env.local`:
const API_KEY = process.env.LIVEKIT_API_KEY;
const API_SECRET = process.env.LIVEKIT_API_SECRET;
const LIVEKIT_URL = process.env.LIVEKIT_URL;
const DEFAULT_AGENT_NAME = process.env.AGENT_NAME;

// don't cache the results
export const revalidate = 0;

export async function POST(req: Request) {
  try {
    if (LIVEKIT_URL === undefined) {
      throw new Error('LIVEKIT_URL is not defined');
    }
    if (API_KEY === undefined) {
      throw new Error('LIVEKIT_API_KEY is not defined');
    }
    if (API_SECRET === undefined) {
      throw new Error('LIVEKIT_API_SECRET is not defined');
    }

    // Parse agent configuration from request body, falling back to env/default.
    const body = await req.json().catch(() => ({}));
    const agentName =
      parseAgentName(body) ??
      (typeof DEFAULT_AGENT_NAME === 'string' && DEFAULT_AGENT_NAME.trim().length > 0
        ? DEFAULT_AGENT_NAME.trim()
        : FALLBACK_AGENT_NAME);

    const preferredLanguage = parseString(body?.language);
    const industry = parseString(body?.industry);
    const requestedVoice = parseRequestedVoice(body?.voice);

    // Generate participant token
    const participantName = 'user';
    const participantIdentity = `voice_assistant_user_${Math.floor(Math.random() * 10_000)}`;
    const roomName = `voice_assistant_room_${Math.floor(Math.random() * 10_000)}`;

    const metadataPayload: Record<string, string> = {};
    if (preferredLanguage) {
      metadataPayload.preferredLanguage = preferredLanguage;
    }
    if (industry) {
      metadataPayload.industry = industry;
    }
    if (requestedVoice) {
      metadataPayload.realtimeVoice = requestedVoice;
    }
    const metadata = Object.keys(metadataPayload).length
      ? JSON.stringify(metadataPayload)
      : undefined;

    const participantToken = await createParticipantToken(
      { identity: participantIdentity, name: participantName, metadata },
      roomName,
      agentName
    );

    // Return connection details
    const data: ConnectionDetails = {
      serverUrl: LIVEKIT_URL,
      roomName,
      participantToken: participantToken,
      participantName,
    };
    const headers = new Headers({
      'Cache-Control': 'no-store',
    });
    return NextResponse.json(data, { headers });
  } catch (error) {
    if (error instanceof Error) {
      console.error(error);
      return new NextResponse(error.message, { status: 500 });
    }
  }
}

function parseAgentName(body: unknown): string | undefined {
  if (!body || typeof body !== 'object') {
    return undefined;
  }

  const roomConfig = (body as { room_config?: unknown; roomConfig?: unknown }).room_config
    ?? (body as { room_config?: unknown; roomConfig?: unknown }).roomConfig;
  if (!roomConfig || typeof roomConfig !== 'object') {
    return undefined;
  }

  const agents = (roomConfig as { agents?: unknown }).agents;
  if (!Array.isArray(agents) || agents.length === 0) {
    return undefined;
  }

  const first = agents[0];
  if (!first || typeof first !== 'object') {
    return undefined;
  }

  const candidate =
    (first as { agent_name?: unknown; agentName?: unknown }).agent_name
    ?? (first as { agent_name?: unknown; agentName?: unknown }).agentName;

  return parseString(candidate);
}

function parseString(value: unknown): string | undefined {
  if (typeof value !== 'string') {
    return undefined;
  }

  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
}

function parseRequestedVoice(value: unknown): string | undefined {
  if (typeof value !== 'string') {
    return undefined;
  }

  return ALLOWED_REALTIME_VOICES.has(value) ? value : undefined;
}

function createParticipantToken(
  userInfo: AccessTokenOptions,
  roomName: string,
  agentName?: string
): Promise<string> {
  const at = new AccessToken(API_KEY, API_SECRET, {
    ...userInfo,
    ttl: '15m',
  });
  const grant: VideoGrant = {
    room: roomName,
    roomJoin: true,
    canPublish: true,
    canPublishData: true,
    canSubscribe: true,
  };
  at.addGrant(grant);

  if (agentName) {
    at.roomConfig = new RoomConfiguration({
      agents: [{ agentName }],
    });
  }

  return at.toJwt();
}
